ROOT_PROMPT = """
Below are the unit exchange rules:
- 1 N = 13 M
- 1 M = 10 P
- 1 P = 5 Q
- 1 Q = 3 G

During the transformation, round the result to two decimal places and show the steps in details.

Below is one example. Given request as `2 N = ? Q`:
1. 2N = 26M because 1N =13M
2. 13M = 130P because 1M=10P
3. 130P = 650Q because 1P=5Q
So 2N = 650Q
"""
