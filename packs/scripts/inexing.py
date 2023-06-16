

data = ["value1", "value2", value3]  # Your data as a list
index_mapping = {0: "key1", 1: "key2", 2: "key3"}  # Index mapping dictionary

# Iterate over the data and retrieve the keys based on indices
for index, value in enumerate(data):
    key = index_mapping.get(index)

    if key:
        # Process the key-value pair
        print(f"Key: {key}, Value: {value}")
    else:
        # Handle indices that are not mapped to keys
        print(f"No mapping found for index: {index}")