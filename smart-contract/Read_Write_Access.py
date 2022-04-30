import smartpy as sp


class Certification(sp.Contract):
    def __init__(self, certifier):
        self.init(
            certifiedRequest=sp.big_map(tkey=sp.TAddress, tvalue=sp.TRecord(
                name=sp.TString, ipfs=sp.TString)),
            submittedRequest=sp.big_map(tkey=sp.TAddress, tvalue=sp.TRecord(
                name=sp.TString, ipfs=sp.TString)),
            certifier=certifier
        )

    @sp.entry_point
    def certify(self, params):
        sp.verify(sp.sender == self.data.certifier)
        self.data.certifiedRequest[params.address] = sp.record(
            name=params.name, ipfs=params.ipfs)

    @sp.entry_point
    def submitRequest(self, params):
        self.data.submittedRequest[params.address] = sp.record(
            name=params.name, ipfs=params.ipfs)


@sp.add_test(name="Certify_test")
def test():
    Tesla = sp.test_account("Tesla")
    BMW = sp.test_account("BMW")

    contract = Certification(certifier=sp.address(
        "tz1YKbquSVyZFP4GupRL5DcDUBRJmqDZMrTw"))

    scenario = sp.test_scenario()
    scenario += contract


sp.add_compilation_target("Certify", Certification(
    certifier=sp.address("tz1YKbquSVyZFP4GupRL5DcDUBRJmqDZMrTw")))
