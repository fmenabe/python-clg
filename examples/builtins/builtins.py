import os
import clg
import yaml

CMD_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__),'builtins.yml'))
cmd = clg.CommandLine(yaml.load(open(CMD_FILE), Loader=yaml.SafeLoader))
args = cmd.parse()
print(args.sum(args.integers))
