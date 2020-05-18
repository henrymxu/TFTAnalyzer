def clean_up_json(dict):
    for key, value in dict.items():
        shops = value["shops"]
        prevShop = {"units": [], "level": 0, "gold": 0}
        temp = []
        while shops:
            x = shops.pop()
            if x["units"] == prevShop["units"]:  # If shops are the same
                continue
            # if "" in x["units"]: # If shop has an empty unit
            #     continue
            temp.append(x)
            prevShop = x
        while temp:
            shops.append(temp.pop())

    for key, value in dict.items():
        sorted_list = sorted(value['shops'], key=lambda k: k['timestamp'])
        print(f"stage: {key}, shop: {sorted_list}")
