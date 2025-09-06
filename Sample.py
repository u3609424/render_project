def mirror_words(x):
   
    # Split the text into words, reverse each word, then join back
    return ' '.join(word[::-1] for word in text.split())

text = "Bank Security"
result = mirror_words(text)
result

