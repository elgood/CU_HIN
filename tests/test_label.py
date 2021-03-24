from src.label import Label

class TestLabel:
    def setup(self):
        self.labeler = Label()
		
    def teardown(self):
        pass

    def test_label_benign_domain(self):
        actual = self.labeler.label("google.com")
        assert actual == 0

    def test_check_for_benign_domain(self):
        actual = self.labeler.check_for_benign_domain("google.com")
        assert actual == True
        
    def test_label_malicious_domain(self):
        actual = self.labeler.label("creativebookmark.com")
        assert actual == 1

    def test_check_for_malicious_domain(self):
        actual = self.labeler.check_for_malicious_domain("creativebookmark.com")
        print(actual)
        assert actual == True

    def test_case_insensitivity(self):
        actual = self.labeler.label("crEATivebookmark.com")
        assert actual == 1

    def test_get_domain_variations(self):
        actual = self.labeler.get_domain_variations("google.com")
        assert "https://www.google.com" in actual
        assert "http://www.google.com" in actual
        assert "www.google.com" in actual

    def test_list_lower(self):
        actual = self.labeler.list_lower(["ABC", "abc", "CDE", "FGE"])
        assert actual == ["abc", "abc", "cde", "fge"]

    def test_get_domain_labels(self):
        actual = self.labeler.get_domain_labels({"google.com": 0, "creativebookmark.com": 1, "crEATivebookmark.com": 2,"test.com": 3})
        assert actual[0,0] == 0
        assert actual[0,1] == 1
        assert actual[1,0] == 1
        assert actual[1,1] == 0
        assert actual[2,0] == 1
        assert actual[2,1] == 0
        assert actual[3,0] == 0
        assert actual[3,1] == 1
