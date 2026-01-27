# Parsing flags (1-bit attributes)
* Save a very basic file as .aepx (it is easier to read than .aep)
* Modify only one value in After Effects, the one that you want to parse
* Open both files in a software that handles diff / comparisons
* Find the byte that changes and it's parent chunk (let's say a 10 becomes 14 in a cdta chunk)
* Find it's position in the chunk data by examining what's before / after (you can use [kaitai web IDE](https://ide.kaitai.io/) for this)
* In `src/kaitai/aep.ksy`, find the corresponding chunk if it exists, otherwise you will need to add it
* Convert your bytes (10 and 14) to binary bits (00001010 and 00001110)
* The bit that you want is the one that changes from 0 to 1, bit number 2 (bit numbers being 7 6 5 4 3 2 1 0)
* In the end, it should look something like this
```
- id: a_value
type: b1  # bit 7
- type: b1  # skip bit 6
- id: a_value
type: b1  # bit 5
- id: a_value
type: b1  # bit 4
- id: a_value
type: b1  # bit 3
- id: YOUR_VALUE
type: b1  # bit 2
- type: b2  # skip bits 1-0
```
* Use [kaitai web IDE](https://ide.kaitai.io/) or [kaitai_struct_compiler](https://github.com/kaitai-io/kaitai_struct_compiler) to compile .ksy file to .py
* Add your flag to a model (Project, Layer, AVItem, CompItem, etc). Refer to [After Effects Scripting Guide](https://ae-scripting.docsforadobe.dev/) for attribute name, attribute's parent class, docstring and type.
* In the corresponding parser, get your data and forward it to the model instance arguments