import smartpy as sp


class Certification(sp.Contract):
    def __init__(self, certifier):
        self.init(
            CANDIDATE=sp.big_map(tkey=sp.TAddress, tvalue=sp.TString),
            CERTIFIED=sp.big_map(tkey=sp.TAddress, tvalue=sp.TString),
            CERTIFIER=certifier.address)

    @sp.entry_point
    def addToCandidate(self, params):
        sp.verify(sp.sender == self.data.CERTIFIER,
                  message="Sender `<sp.sender>` is not certifier")
        self.data.CANDIDATE[params.address] = params.name

    @sp.entry_point
    def certify(self, params):
        sp.verify(sp.sender == self.data.CERTIFIER,
                  message="Sender `<sp.sender>` is not certifier")
        sp.verify((self.data.CANDIDATE.contains(params.address)),
                  message="Please first add `<params.name>` to candidate list")
        self.data.CERTIFIED[params.address] = params.name


@sp.add_test(name="Certify")
def test():
    ADMIN = sp.test_account("ADMIN")
    BMW = sp.test_account("BMW")
    TESLA = sp.test_account("TESLA")

    scenario = sp.test_scenario()
    scenario.h2("Accounts")
    scenario.show([ADMIN, BMW, TESLA])

    contract = Certification(certifier=ADMIN)

    scenario += contract
    scenario += contract.addToCandidate(name=BMW.seed,
                                        address=BMW.address).run(sender=ADMIN)
    scenario += contract.certify(name=BMW.seed,
                                 address=BMW.address).run(sender=ADMIN)
    scenario += contract.certify(name=TESLA.seed,
                                 address=TESLA.address).run(sender=ADMIN)
