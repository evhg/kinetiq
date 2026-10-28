"""Run a shot with constant overrides: k12_run.py shots/K01-hero-beam.py NAME=value ... -- <shot args>"""
import sys, importlib.util, os
script = sys.argv[1]
i = sys.argv.index("--")
over = sys.argv[2:i]
sys.argv = [script] + sys.argv[i + 1:]
sys.path.insert(0, os.path.dirname(os.path.abspath(script)))
spec = importlib.util.spec_from_file_location("shot", script)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
for kv in over:
    k, v = kv.split("=", 1)
    setattr(m, k, eval(v))
    print("override", k, "=", v)
m.main()
