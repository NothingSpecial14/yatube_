from django import template

register=template.Library()

@register.filter
def addclass(field, css):
    return field.as_widget(attrs={"class":css})

# @register.filter
# def uglify(field):
#     strfield=str(field)
#     res=''
#     for i in range(len(strfield)):
#         if i % 2==0:
#             res+=strfield[i].upper()
#         else:
#             res+=strfield[i].lower()
#     return res