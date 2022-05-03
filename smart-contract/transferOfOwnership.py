import smartpy as sp

# Import FA2 template
FA2 = sp.io.import_script_from_url("https://smartpy.io/dev/templates/FA2.py")


class Token(FA2.FA2):
    pass

# our admin
# intended feature - Minting NFT
# Collecting NFT
# Transfering XTZ from contract to account. i.e. Collecting management rewards
# Updating admin

# Example
# admin - Envited Marketplace
# buyer - BMW
# seller - repair shop center


class Marketplace(sp.Contract):
    def __init__(self, token, metadata, admin):
        self.init(
            token=token,
            metadata=metadata,
            admin=admin,
            data=sp.big_map(tkey=sp.TNat, tvalue=sp.TRecord(
                holder=sp.TAddress, author=sp.TAddress, amount=sp.TNat, token_id=sp.TNat, collectable=sp.TBool)),
            token_id=0,
        )

    @sp.entry_point
    def mint(self, params):
        sp.verify((params.amount > 0))
        # Cast an address to a typed contract​
        contract = sp.contract(
            sp.TRecord(
                address=sp.TAddress,
                amount=sp.TNat,
                token_id=sp.TNat,
                # we are sending metadata to the token contract
                metadata=sp.TMap(sp.TString, sp.TBytes)
            ),
            self.data.token,
            # expr.open_some() to get optional value
            entry_point="mint").open_some()

        #sp.transfer(arg, amount, destination)
        # destination must be of type contract
        # arg sent to the destination must be what the contract expects
        # in our case, args must be of type record
        sp.transfer(
            sp.record(
                address=sp.self_address,
                amount=1,
                token_id=self.data.token_id,
                metadata={'': params.metadata}
            ),
            sp.mutez(0),
            contract)

        self.data.data[self.data.token_id] = sp.record(
            holder=sp.self_address, author=sp.sender, amount=params.amount, token_id=self.data.token_id, collectable=True)
        self.data.token_id += 1

    @sp.entry_point
    def collect(self, params):
        # to verify amount of transaction is equal to cost of nft
        # to verify the nft was on sale -- colleactable - True
        sp.verify(((sp.amount == sp.utils.nat_to_mutez(self.data.data[params.token_id].amount)) & (self.data.data[params.token_id].amount != 0) & (
            self.data.data[params.token_id].collectable == True) & (self.data.data[params.token_id].author != sp.sender)))
        self.data.data[params.token_id].collectable = False
        self.data.data[params.token_id].holder = sp.sender

        self.fa2_transfer(self.data.token, sp.self_address,
                          sp.sender, params.token_id, 1)

    @sp.entry_point
    def update_admin(self, params):
        # only admin can modify admin role
        sp.verify(sp.sender == self.data.admin)
        self.data.admin = params

    # util function to call transfer entry point in the token contract
    # contaning contract address and info about the token transfer
    def fa2_transfer(self, fa2, from_, to_, token_id, amount):
        contract = sp.contract(sp.TList(
            sp.TRecord(from_=sp.TAddress,
                       txs=sp.TList(
                           sp.TRecord(amount=sp.TNat,
                                      to_=sp.TAddress,
                                      token_id=sp.TNat).layout(("to_", ("token_id", "amount")))))), fa2, entry_point='transfer').open_some()
        sp.transfer(sp.list([sp.record(from_=from_, txs=sp.list(
            [sp.record(amount=amount, to_=to_, token_id=token_id)]))]), sp.mutez(0), contract)


@sp.add_test(name="Non Fungible Token")
def test():
    scenario = sp.test_scenario()

    ADMIN = sp.test_account("admin")
    SECOND_ADMIN = sp.test_account("second admin")
    BMW = sp.test_account("bmw")
    TESLA = sp.test_account("tesla")
    CONTI = sp.test_account("conti")

    scenario.show([ADMIN, ANOTHER_ADMIN, BMW, TESLA, CONTI])

    token_contract = Token(FA2.FA2_config(non_fungible=True), admin=ADMIN.address, metadata=sp.utils.metadata_of_url(
        "ipfs://QmRYy8Mq576hPsLHMy7WQdEWvRo2NoHhGVj89dE1n4dAKg"))

    scenario += token_contract

    scenario.h1("MarketPlace")
    marketplace = Marketplace(token_contract.address, sp.utils.metadata_of_url(
        "ipfs://QmRYy8Mq576hPsLHMy7WQdEWvRo2NoHhGVj89dE1n4dAKg"), ADMIN.address)
    scenario += marketplace
    scenario.h1("Mint")

    # test to mint without admin access for marketplace
    scenario += marketplace.mint(sp.record(amount=10, metadata=sp.pack(
        "ipfs://QmbQDdDejtN9BVsF6p51xg8LR5csn2uGqbgqWhZAvgeae5/test_data.json"))).run(sender=ADMIN, valid=False)

    # add admin access for marketplace
    scenario += token_contract.set_administrator(
        marketplace.address).run(sender=ADMIN)
    scenario += marketplace.mint(sp.record(amount=10, metadata=sp.pack(
        "ipfs://QmbQDdDejtN9BVsF6p51xg8LR5csn2uGqbgqWhZAvgeae5/test_data.json"))).run(sender=ADMIN)
    scenario += marketplace.mint(sp.record(amount=10,
                                           metadata=sp.pack("123423"))).run(sender=BMW)
    # collect nft
    scenario.h1("Collect")
    scenario += marketplace.collect(sp.record(token_id=0)
                                    ).run(sender=CONTI, amount=sp.mutez(10))

    # update admin
    scenario += marketplace.update_admin(
        (SECOND_ADMIN.address)).run(sender=ADMIN)
