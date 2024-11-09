import subprocess

def run_script(commands):
    raw_output = None
    process = subprocess.Popen(['./build/main'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for command in commands:
        process.stdin.write(command + '\n')

    process.stdin.close()

    # Read entire output
    raw_output = process.stdout.read()
    process.stdout.close()
    process.stderr.close()

    return raw_output.split('\n')

def test_inserts_and_retrieves_row():
    result = run_script([
        "insert 1 user1 person1@example.com",
        "select",
        ".exit",
    ])
    expected_output = [
        "db > Executed.",
        "db > (1, user1, person1@example.com)",
        "Executed.",
        "db > ",
    ]
    return result == expected_output

def test_insert_large_number_of_row():
    script = [f"insert {i} user{i} person{i}@example.com" for i in range(1401)]
    script.append(".exit")
    result = run_script(script)
    expected_output = [
        "db > Error: Table full.",
    ]
    return result == expected_output 
     

def test_insert_large_number_of_row():
    script = [f"insert {i} user{i} person{i}@example.com" for i in range(1,130)]
    script.append(".exit")
    result = run_script(script)
    print(f"length : {len(result)}")
    expected_output = [
        "db > Error: Table full.",
    ]
    return result == expected_output 

def allows_inserting_strings_that_are_the_maximum_length():
    long_name = "a"*32
    long_email = "a"*255
    result = run_script([
        f"insert 1 {long_name} {long_email}",
        "select",
        ".exit",
    ])
    expected_output = [
        "db > Executed.",
        f"db > (1, {long_name}, {long_email})",
        "Executed.",
        "db > ",
    ]
    return result == expected_output 

def prints_error_message_if_strings_are_too_long():
    long_username = "a"*33
    long_email = "a"*256
    script = [
        f"insert 1 {long_username} {long_email}",
        "select",
        ".exit",
    ]
    result = run_script(script)
    expected_output = [
        "db > String is too long.",
        "db > Executed.",
        "db > ",
    ]
    return result == expected_output

def prints_an_error_message_if_id_is_negative():
    script = [
        "insert -1 cstack foo@bar.com",
        "select",
        ".exit",
    ]
    result = run_script(script)
    expected_output = [
        "db > ID must be positive.",
        "db > Executed.",
        "db > ",
    ]
    return result == expected_output

def keeps_data_after_closing_connection():
    script = [
        "insert 1 cstack foo@bar.com",
        ".exit",
    ]
    result_1 = run_script(script)
    expected_output_1 = [
        "db > Executed.",
        "db > ",
    ]
    script = [
        "select",
        ".exit",
    ]
    result_2 = run_script(script)
    expected_output_2 = [
        "db > (1, cstack, foo@bar.com)",
        "db > Executed.",
        "db > ",
    ]
    return result_2 == expected_output_2 and result_1 == expected_output_1

def main(): 
    tests = [
        test_inserts_and_retrieves_row, allows_inserting_strings_that_are_the_maximum_length, prints_error_message_if_strings_are_too_long, 
        prints_an_error_message_if_id_is_negative,
        keeps_data_after_closing_connection
    ] 
    successful_tests = 0 
    failed_tests = 0 
    for test in tests: 
        success = test()
        if success: 
            successful_tests += 1 
        else: 
            failed_tests += 1 
            print(f"Test {test.__name__} failed.") 
            # print(f"Ouput:\n{result}")
    print(f"{successful_tests} tests passed.") 
    print(f"{failed_tests} tests failed.") 

if __name__ == "__main__":
    main()