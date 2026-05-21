monster_health = 50

def attack_monster(monster_label, result_label):
    global monster_health

    damage = 10
    monster_health -= damage

    if monster_health <= 0:
        monster_health = 0
        result_label.config(text="Monster defeated!")

    monster_label.config(
        text=f"Monster HP: {monster_health}"
    )