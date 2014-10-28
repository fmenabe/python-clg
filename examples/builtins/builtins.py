import clg
import yaml

cmd = clg.CommandLine(yaml.load(open('builtins.yml')))
args = cmd.parse()
print(args.sum(args.integers))
