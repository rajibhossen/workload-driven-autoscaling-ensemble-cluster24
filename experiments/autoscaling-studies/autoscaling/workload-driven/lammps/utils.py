

def change_minicluster_size(filename, value):
    with open(filename, 'r') as file:
        filedata = file.read()
    size_index = filedata.find('size: ')
    current_line = filedata[size_index:size_index + 7]
    print(current_line)
    # Replace the target string
    filedata = filedata.replace(current_line, 'size: ' + str(value))

    # Write the file out again
    with open(filename, 'w') as file:
        file.write(filedata)

    print("Updated Size: ", value)
    print("Done writing")
