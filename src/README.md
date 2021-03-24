## Hindom Experiment
Source files are in this directory.


## Labeling Domains

In order to label domains, use the label class:

```
from src.label import Label

labeler = Label()
domain_to_index = {"google.com": 0, "test.com": 1}
matrix = labeler.get_domain_labels(domain_to_index)
```

### Understanding Label Output

The malicious column is the first column, or 0th indexed column of the matrix, and the benign column is the second column, or the 1st indexed column of the matrix.

- If domain is on blacklist --> [1, 0]
- If domain is on whitelist --> [0, 1]
- If domain is on both blacklist and whitelist --> [1, 0]
- If domain is on neither blacklist and whitelist --> [0, 0]
