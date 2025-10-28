# Python script to replace text in a large file

# Step 1: Open the file in read mode
with open('fontawesome.min.css', 'r', encoding='utf-8') as file:
    file_data = file.read()  # Read the contents of the file

# Step 2: Replace the target string
file_data = file_data.replace('https://cdnjs.cloudflare.com/', '../webfonts/')

# Step 3: Write the modified contents back to the file
with open('fontawesome.min.css', 'w', encoding='utf-8') as file:
    file.write(file_data)

print("Replacement completed successfully!")
