# Spot check: 'random 20 prepend' on three April malware reports (decoded tokens)

Rebuilt independently (baseline/audit_independent.py) from the call-token store with the stored sampler definition (`default_rng([6000, April row, 20, 1])`; per call a uniform report of the 3,161 held-out benign pool reports, then a uniform call of it) and decoded with the SentencePiece model of the corrected tokenizer. Order of an edited report: the report's own header tokens, then the 20 added calls, then the original calls and the tail. The model reads the first 512 tokens. Rule for the choice: the first three April malware reports (lowest April row) with at least 20 calls. No selection on any score.

## April row 0 (malware; 501 original calls, 2232 tokens unedited, 2351 tokens edited)

- header tokens of the original report: positions 0 to 0; the 20 added calls: positions 1 to 119 (119 tokens); **the original report's calls start at token position 120** (0-based); the edit starts at position 1; the unedited and the edited model input first differ at position 2 (earlier tokens coincide because many calls begin with the same tokens).
- the added calls come from the held-out benign pool reports: 22376:26, 31281:149, 28874:254, 28309:103, 20513:54, ... (store row : call index)

**First 120 tokens, decoded:**

```
apis kernel32 heapalloc 0x45f0 0x0 0x20 0x4e50 kernel32 lcmapstringex 0x0 0x200 0x1211748 0x5 0x1211728 0x5 0x0 0x0 0x0 0x5 kernel32 leavecriticalsection 0x58c01c none kernel32 initializecriticalsectionex 0x79c0 0xfa0 0x0 0x1 api ms win crt heap l1 1 0 malloc 0x24 0x4840 kernel32 getlasterror 0x0 kernel32 flsalloc 0x418210 0x1 kernel32 getversion 0x1db10106 user32 charnextw 0x40a57e 0x40a580 kernel32 getcurrentthreadid 0x139a0 kernel32 heaprealloc 0x45f0 0x0 0x99e0 0x200 0x9cc0 user32 charnexta 0x45f9 0x45fa kernel32 isprocessorfeaturepresent pf xmmi64 instructions available 0x1 kernel32 getprocaddress 0x77000000 getprocessaffinitymask 0xfeee0000 kernel32 entercriticalsection 0x5392f8 none kernel32 initializecriticalsectionex 0x7690 0xfa0 0x0 0x1 kernel32 initializecriticalsectionex 0x7090 0xfa0 0x0 0x1 msvbvm50 ordinal 100 0x4014c4 0xfeedf000 0x4000 0x4010 0x0 kernel32 initializecriticalsectionex 0x7990 0xfa0 0x0 0x1 kernel32 heapalloc 0x45f0 0x0 0x10 0x8ed0
```

**Segments inside the first 120 tokens** (position range: decoded text):

- 0-0 header of the original report: `apis`
- 1-6 added call 1: `kernel32 heapalloc 0x45f0 0x0 0x20 0x4e50`
- 7-18 added call 2: `kernel32 lcmapstringex 0x0 0x200 0x1211748 0x5 0x1211728 0x5 0x0 0x0 0x0 0x5`
- 19-22 added call 3: `kernel32 leavecriticalsection 0x58c01c none`
- 23-28 added call 4: `kernel32 initializecriticalsectionex 0x79c0 0xfa0 0x0 0x1`
- 29-39 added call 5: `api ms win crt heap l1 1 0 malloc 0x24 0x4840`
- 40-42 added call 6: `kernel32 getlasterror 0x0`
- 43-46 added call 7: `kernel32 flsalloc 0x418210 0x1`
- 47-49 added call 8: `kernel32 getversion 0x1db10106`
- 50-53 added call 9: `user32 charnextw 0x40a57e 0x40a580`
- 54-57 added call 10: `kernel32 getcurrentthreadid 0x139a0`
- 58-64 added call 11: `kernel32 heaprealloc 0x45f0 0x0 0x99e0 0x200 0x9cc0`
- 65-68 added call 12: `user32 charnexta 0x45f9 0x45fa`
- 69-75 added call 13: `kernel32 isprocessorfeaturepresent pf xmmi64 instructions available 0x1`
- 76-80 added call 14: `kernel32 getprocaddress 0x77000000 getprocessaffinitymask 0xfeee0000`
- 81-85 added call 15: `kernel32 entercriticalsection 0x5392f8 none`
- 86-91 added call 16: `kernel32 initializecriticalsectionex 0x7690 0xfa0 0x0 0x1`
- 92-97 added call 17: `kernel32 initializecriticalsectionex 0x7090 0xfa0 0x0 0x1`
- 98-107 added call 18: `msvbvm50 ordinal 100 0x4014c4 0xfeedf000 0x4000 0x4010 0x0`
- 108-113 added call 19: `kernel32 initializecriticalsectionex 0x7990 0xfa0 0x0 0x1`
- 114-119 added call 20: `kernel32 heapalloc 0x45f0 0x0 0x10 0x8ed0`

**Boundary excerpt, tokens 105 to 164 (the last tokens of the added calls, then the original report's calls):**

```
0x4000 0x4010 0x0 kernel32 initializecriticalsectionex 0x7990 0xfa0 0x0 0x1 kernel32 heapalloc 0x45f0 0x0 0x10 0x8ed0 kernel32 getsystemtimeasfiletime 0x1211fd8 none kernel32 getcurrentprocessid 0xdcb4 kernel32 getcurrentthreadid 0xdcc8 kernel32 gettickcount 0x5265c14 kernel32 queryperformancecounter 0x1211fd0 0x1 kernel32 getprocessheap 0x45f0 kernel32 heapalloc 0x45f0 0x0 0x94 0x4610 kernel32 getversionexa 0x4610 0x1 kernel32 getprocessheap 0x45f0 kernel32 heapfree 0x45f0 0x0 0x4610 0x1 kernel32 heapcreate 0x0 0x1000
```

## April row 1 (malware; 501 original calls, 2239 tokens unedited, 2356 tokens edited)

- header tokens of the original report: positions 0 to 0; the 20 added calls: positions 1 to 117 (117 tokens); **the original report's calls start at token position 118** (0-based); the edit starts at position 1; the unedited and the edited model input first differ at position 3 (earlier tokens coincide because many calls begin with the same tokens).
- the added calls come from the held-out benign pool reports: 12887:0, 13289:0, 25875:157, 12163:25, 13036:1, ... (store row : call index)

**First 120 tokens, decoded:**

```
apis kernel32 getmodulehandlea 0x0 0x400000 xpprt1 xpprt1version 0x0 0x0 0x0 0x1212000 0x0 user32 charnextw 0x40a584 0x40a586 kernel32 initializecriticalsectionex 0x4394b8 0xfa0 0x0 0x1 rtl100 system initialization qqrv 0x40176e 0x0 0xfeedf000 0x4000 0x0 user32 charnextw 0x4cb020 0x4cb022 kernel32 decodepointer 0xfeee0007 0xfeee0006 kernel32 getprocaddress 0x77000000 encodepointer 0xfeee0004 kernel32 getcurrentthreadid 0x2d14 msvcrt controlfp 0x10000 0x30000 0x0 msvcrt initterm 0x47b008 0x47b00c 0x0 kernel32 queryperformancecounter 0x5627fcc 0x1 kernel32 heapalloc 0x45f0 0x0 0x8 0x8ec0 kernel32 getprocaddress 0x77000000 flsfree 0xfeee0003 kernel32 multibytetowidechar 0x4e4 0x1 0x1 0x0 0x0 0x1 kernel32 getstartupinfow 0x169bf68 none shell32 shgetfileinfow 0x42b228 0x0 0x1211d50 0x2b4 0x0 kernel32 initializecriticalsectionex 0x42d3d8 0xfa0 0x0 0x1 kernel32 initializecriticalsectionex 0x7a20 0xfa0 0x0 0x1 c60runx sysinit 0xfeedf000 0x4000 0x4010 0x4020 0x0 kernel32 getmodulehandlea
```

**Segments inside the first 120 tokens** (position range: decoded text):

- 0-0 header of the original report: `apis`
- 1-4 added call 1: `kernel32 getmodulehandlea 0x0 0x400000`
- 5-11 added call 2: `xpprt1 xpprt1version 0x0 0x0 0x0 0x1212000 0x0`
- 12-15 added call 3: `user32 charnextw 0x40a584 0x40a586`
- 16-21 added call 4: `kernel32 initializecriticalsectionex 0x4394b8 0xfa0 0x0 0x1`
- 22-32 added call 5: `rtl100 system initialization qqrv 0x40176e 0x0 0xfeedf000 0x4000 0x0`
- 33-36 added call 6: `user32 charnextw 0x4cb020 0x4cb022`
- 37-40 added call 7: `kernel32 decodepointer 0xfeee0007 0xfeee0006`
- 41-45 added call 8: `kernel32 getprocaddress 0x77000000 encodepointer 0xfeee0004`
- 46-49 added call 9: `kernel32 getcurrentthreadid 0x2d14`
- 50-54 added call 10: `msvcrt controlfp 0x10000 0x30000 0x0`
- 55-61 added call 11: `msvcrt initterm 0x47b008 0x47b00c 0x0`
- 62-66 added call 12: `kernel32 queryperformancecounter 0x5627fcc 0x1`
- 67-72 added call 13: `kernel32 heapalloc 0x45f0 0x0 0x8 0x8ec0`
- 73-77 added call 14: `kernel32 getprocaddress 0x77000000 flsfree 0xfeee0003`
- 78-85 added call 15: `kernel32 multibytetowidechar 0x4e4 0x1 0x1 0x0 0x0 0x1`
- 86-89 added call 16: `kernel32 getstartupinfow 0x169bf68 none`
- 90-96 added call 17: `shell32 shgetfileinfow 0x42b228 0x0 0x1211d50 0x2b4 0x0`
- 97-102 added call 18: `kernel32 initializecriticalsectionex 0x42d3d8 0xfa0 0x0 0x1`
- 103-108 added call 19: `kernel32 initializecriticalsectionex 0x7a20 0xfa0 0x0 0x1`
- 109-117 added call 20: `c60runx sysinit 0xfeedf000 0x4000 0x4010 0x4020 0x0`
- 118-142 original calls begin: `kernel32 getmodulehandlea kernel32 0x77000000 kernel32 getprocaddress 0x77000000 virtualprotect 0xfeee0000 kernel32 virtualprotect 0x40015f 0x78 0x4 0x1211fc4 0x1 kernel32 virtualprotect 0x40015f 0x78 0x40 0x1211fc4 0x1 kernel32 getmodulehandlea`

**Boundary excerpt, tokens 103 to 162 (the last tokens of the added calls, then the original report's calls):**

```
kernel32 initializecriticalsectionex 0x7a20 0xfa0 0x0 0x1 c60runx sysinit 0xfeedf000 0x4000 0x4010 0x4020 0x0 kernel32 getmodulehandlea kernel32 0x77000000 kernel32 getprocaddress 0x77000000 virtualprotect 0xfeee0000 kernel32 virtualprotect 0x40015f 0x78 0x4 0x1211fc4 0x1 kernel32 virtualprotect 0x40015f 0x78 0x40 0x1211fc4 0x1 kernel32 getmodulehandlea advapi32 dll 0x78000000 kernel32 getprocaddress 0x78000000 regsetvalueexa 0xfeee0001 kernel32 getprocaddress 0x78000000 lookupprivilegevaluea 0xfeee0002 kernel32 getprocaddress 0x78000000 regopenkeya 0xfeee0003 kernel32 getprocaddress
```

## April row 2 (malware; 143 original calls, 715 tokens unedited, 823 tokens edited)

- header tokens of the original report: positions 0 to 0; the 20 added calls: positions 1 to 108 (108 tokens); **the original report's calls start at token position 109** (0-based); the edit starts at position 1; the unedited and the edited model input first differ at position 2 (earlier tokens coincide because many calls begin with the same tokens).
- the added calls come from the held-out benign pool reports: 29831:146, 20046:171, 15530:77, 75094:6, 35112:178, ... (store row : call index)

**First 120 tokens, decoded:**

```
apis kernel32 entercriticalsection 0x5e4a0f0 none user32 charnextw 0x40a5aa 0x40a5ac kernel32 initializecriticalsectionex 0x74e0 0xfa0 0x0 0x1 kernel32 getmodulehandlew 0x0 0x400000 user32 charnextw 0x40a932 0x40a934 kernel32 initializecriticalsection 0x41f8c14 none kernel32 entercriticalsection 0x598740 none kernel32 getprocaddress 0x77000000 wakeallconditionvariable 0xfeee001c kernel32 getmodulehandlea 0x0 0x400000 kernel32 lcmapstringw 0x0 0x100 0x169b780 0x102 0x169b57c 0x102 0x102 kernel32 setdefaultdlldirectories 0x800 0x1 user32 charnexta 0x45f2 0x45f3 kernel32 entercriticalsection 0x2c3dbd0 none kernel32 getmodulehandlea 0x0 0x400000 kernel32 getmodulehandlea 0x0 0x400000 msvbvm50 ordinal 100 0x4119a8 0xfeedf000 0x4000 0x4010 0x0 kernel32 initializecriticalsectionex 0x447060 0xfa0 0x0 0x1 kernel32 initializecriticalsectionex 0x7b70 0xfa0 0x0 0x1 user32 wsprintfw vie dll s s dll 0x29 msvcrt initterm 0x4ad0836c 0x4ad08374 0x0 kernel32 loadlibrarya kernel32 dll 0x77000000 kernel32 getprocaddress 0x77000000 localrealloc 0xfeee0000 kernel32
```

**Segments inside the first 120 tokens** (position range: decoded text):

- 0-0 header of the original report: `apis`
- 1-5 added call 1: `kernel32 entercriticalsection 0x5e4a0f0 none`
- 6-9 added call 2: `user32 charnextw 0x40a5aa 0x40a5ac`
- 10-15 added call 3: `kernel32 initializecriticalsectionex 0x74e0 0xfa0 0x0 0x1`
- 16-19 added call 4: `kernel32 getmodulehandlew 0x0 0x400000`
- 20-23 added call 5: `user32 charnextw 0x40a932 0x40a934`
- 24-29 added call 6: `kernel32 initializecriticalsection 0x41f8c14 none`
- 30-33 added call 7: `kernel32 entercriticalsection 0x598740 none`
- 34-38 added call 8: `kernel32 getprocaddress 0x77000000 wakeallconditionvariable 0xfeee001c`
- 39-42 added call 9: `kernel32 getmodulehandlea 0x0 0x400000`
- 43-51 added call 10: `kernel32 lcmapstringw 0x0 0x100 0x169b780 0x102 0x169b57c 0x102 0x102`
- 52-55 added call 11: `kernel32 setdefaultdlldirectories 0x800 0x1`
- 56-59 added call 12: `user32 charnexta 0x45f2 0x45f3`
- 60-63 added call 13: `kernel32 entercriticalsection 0x2c3dbd0 none`
- 64-67 added call 14: `kernel32 getmodulehandlea 0x0 0x400000`
- 68-71 added call 15: `kernel32 getmodulehandlea 0x0 0x400000`
- 72-81 added call 16: `msvbvm50 ordinal 100 0x4119a8 0xfeedf000 0x4000 0x4010 0x0`
- 82-87 added call 17: `kernel32 initializecriticalsectionex 0x447060 0xfa0 0x0 0x1`
- 88-93 added call 18: `kernel32 initializecriticalsectionex 0x7b70 0xfa0 0x0 0x1`
- 94-101 added call 19: `user32 wsprintfw vie dll s s dll 0x29`
- 102-108 added call 20: `msvcrt initterm 0x4ad0836c 0x4ad08374 0x0`
- 109-133 original calls begin: `kernel32 loadlibrarya kernel32 dll 0x77000000 kernel32 getprocaddress 0x77000000 localrealloc 0xfeee0000 kernel32 getprocaddress 0x77000000 deletecriticalsection 0xfeee0001 kernel32 getprocaddress 0x77000000 globalfree 0xfeee0002 kernel32 getprocaddress 0x77000000 tlsfree 0xfeee0003`

**Boundary excerpt, tokens 94 to 153 (the last tokens of the added calls, then the original report's calls):**

```
user32 wsprintfw vie dll s s dll 0x29 msvcrt initterm 0x4ad0836c 0x4ad08374 0x0 kernel32 loadlibrarya kernel32 dll 0x77000000 kernel32 getprocaddress 0x77000000 localrealloc 0xfeee0000 kernel32 getprocaddress 0x77000000 deletecriticalsection 0xfeee0001 kernel32 getprocaddress 0x77000000 globalfree 0xfeee0002 kernel32 getprocaddress 0x77000000 tlsfree 0xfeee0003 kernel32 getprocaddress 0x77000000 getprocaddress 0xfeee0004 kernel32 getprocaddress 0x77000000 interlockeddecrement 0xfeee0005 kernel32 getprocaddress 0x77000000 freelibrary 0xfeee0006 kernel32 getprocaddress 0x77000000 getcurrentprocessid 0xfeee0007
```

