from src.label import Label

class TestLabel:
    def setup(self):
        self.label = Label()
		
    def teardown(self):
        pass

    def test_if_domain_is_good(self):

        actual = self.label.getDomainLabel("google.com")
        assert actual == "good"
        
    def test_if_domain_is_bad(self):
        actual = self.label.getDomainLabel("creativebookmark.com")
        assert actual == "malicious"

    def test_that_case_doesnt_matter(self):
        actual = self.label.getDomainLabel("crEATivebookmark.com")
        assert actual == "malicious"






