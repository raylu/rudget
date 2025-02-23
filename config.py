import tomllib

class TOMLAttrs:
	pass

def set_attrs(target, d):
	for k, v in d.items():
		if isinstance(v, dict):
			target[k] = TOMLAttrs()
			set_attrs(target[k].__dict__, v)
		else:
			target[k] = v

with open('config.toml', 'rb') as f:
	doc = tomllib.load(f)
set_attrs(globals(), doc)
