import random
pass_length = 12
pass_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#+-/*"

password = "".join(random.choices(pass_chars, k=pass_length))

print(password)
