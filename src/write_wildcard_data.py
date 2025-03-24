def ask(question): return input(f'\n{question}\n> ')

common_string = ask('Common string to write for each file (include *)')
if '*' not in common_string: exit('Missing wildcard symbol *')
value_range = ask('Inclusive range of values to replace wildcard with \n'
                  + '- Numerical range: hyphen-separated (e.g. 0-99) \n'
                  + '- Otherwise: comma-separated (e.g. a, b, c)')
if ',' in value_range:
    value_range = [str.strip(x) for x in value_range.split(',')]
elif '-' in value_range:
    try: [start, stop] = [str.strip(x) for x in value_range.split('-')]
    except: exit('Not a valid range')
    value_range = range(int(start), int(stop) + 1)
else: exit('Not a valid range')
text = ''
for value in value_range: text += f"{common_string.replace('*', str(value))}\n"
output_name = ask('Output name (data/<user_input>.txt)')
output_name = f'data/{output_name}.txt'
with open(output_name, 'w') as outfile: outfile.write(text)
print(f'Wrote {len(value_range)} lines to {output_name}')