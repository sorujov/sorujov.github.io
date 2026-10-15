"""python texts.py lectureN.py out.json -> {md5: narration} for every self.say("...") call."""
import ast
import hashlib
import json
import sys

tree = ast.parse(open(sys.argv[1]).read())
xs = []
for n in ast.walk(tree):
    if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "say" and n.args and isinstance(n.args[0], ast.Constant):
        xs.append(n.args[0].value)
    if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "title_card" and len(n.args) == 3:
        xs.append(n.args[2].value)
d = {hashlib.md5(x.encode()).hexdigest(): x for x in xs}
json.dump(d, open(sys.argv[2], "w"), ensure_ascii=False)
print(len(d), "clips,", sum(map(len, d.values())), "characters")
