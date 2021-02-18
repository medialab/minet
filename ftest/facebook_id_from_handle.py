from minet.facebook import page_id_from_handle, group_id_from_handle

HANDLES = [
    ('DonaldDuck', 'page'),
    ('astucerie', 'page'),
    ('ps.avenches', 'group')
]

for handle, t in HANDLES:
    if t == 'page':
        result = page_id_from_handle(handle)
    else:
        result = group_id_from_handle(handle)

    print(result)
