from app import app

print("Flask Routes:")
for rule in app.url_map.iter_rules():
    print(f"{rule.rule} -> {rule.endpoint} ({', '.join(rule.methods)})") 