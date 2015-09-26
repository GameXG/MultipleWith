# MultipleWith
python MultipleWith

``` python

from multiplewith import MultipleWith
with MultipleWith( open('/path0','rb'),
                   open('/path1','wb')) as file_list:
  file_list[1].write(file_list[0].read())
  
with MultipleWith( ('file0',open('/path0','rb')),
                   ('file1',open('/path1','wb')),) as file_dict:
  file_dict['file1'].write(file_dict[file0].reas())
  
with MultipleWith( file0=open('/path0','rb'),
                   file1=open('/path1','wb'),) as file_dict:
  file_dict['file1'].write(file_dict[file0].reas())

```
