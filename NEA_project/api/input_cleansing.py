def input_cleansing(input_string, is_email=False):
    invalid_characters = [";", "(", ")", "{", "}", "[", "]", "<", ">", "|", "\\", "^", '"'
                              "`", "~", "!", "#", "%", "^", "*", "+", "=", ":", "?", "/"]
    inavlid_email_characters = [';', '(', ')', '<', '>', '[', ']', '\\', ',', ':', '"', ' ', '*']
    # invalid characters differ with email and other string
    if is_email:
        for x in range(len(input_string)):
            if input_string[x] in inavlid_email_characters:
                return False
    else:
        for x in range(len(input_string)):
            if input_string[x] in invalid_characters:
                return False
    return True