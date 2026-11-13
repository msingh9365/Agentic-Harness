# Why April ransomware and coinminer reports are missed (analyze_misses.py)

## 0. Checks

- Test rows joined to `meta.csv`; the order rebuilt independently from `list_files()` is identical for all 92,700 reports, and labels match `test_scores.csv` for all 17,402 test rows.
- `finetune_k8` test AUC 0.9639 (REPORT §7: 0.9639); per-chunk-bucket AUCs 1: 0.9726, 2–3: 0.9817, 4–8: 0.9358 reproduced.
- Threshold at 1% FPR on the 8,003 April benign reports: `finetune_k8` 0.99896 (flags 80), `frozen_k1` 0.87452 (flags 80).

## 1. Detection per family (reproduces preliminary finding 1)

| family | April reports | flagged by finetune_k8 | flagged by frozen_k1 |
|---|---|---|---|
| backdoor | 1,940 | 80.0% (1,552) | 82.2% (1,595) |
| clean | 7,944 | 1.0% (80) | 1.0% (80) |
| coinminer | 1,684 | 66.3% (1,116) | 79.5% (1,339) |
| dropper | 252 | 77.4% (195) | 71.8% (181) |
| keylogger | 1,041 | 88.1% (917) | 64.4% (670) |
| ransomware | 2,139 | 60.4% (1,293) | 66.5% (1,422) |
| rat | 1,258 | 84.8% (1,067) | 83.9% (1,056) |
| trojan | 1,085 | 80.9% (878) | 79.8% (866) |
| windows_syswow64 | 59 | 0.0% (0) | 0.0% (0) |

`finetune_k8` misses 2,381 of 9,399 April malware reports; ransomware + coinminer cause 59.4% (1,414) of them (ransomware 846, coinminer 568).

## 1b. Preliminary findings recomputed with the preliminary definitions

Same data and definitions as the first analysis (`results/samples.csv` columns and the coarse fingerprint); exact-hash versions follow in later sections.

| finding | quantity | preliminary | recomputed |
|---|---|---|---|
| 1 | misses of finetune_k8 | 2,381 | 2,381 |
| 1 | ransomware + coinminer share of misses | 59% | 59.4% |
| 1 | ransomware detection finetune_k8 vs frozen_k1 | 60.4% vs 66.5% | 60.4% vs 66.5% |
| 1 | coinminer detection finetune_k8 vs frozen_k1 | 66.3% vs 79.5% | 66.3% vs 79.5% |
| 2 | ransomware file_access present, missed vs caught (tok_file_access > 0) | 1.4% vs 36.3% | 1.4% vs 36.3% |
| 2 | ransomware >1 entry point, missed vs caught | 0.1% vs 33.6% | 0.1% vs 33.6% |
| 2 | ransomware median API calls (n_apis_raw), missed vs caught | about 140 both | 142 vs 142 |
| 3 | largest coarse fingerprint among coinminer misses | 265 of 568 (47%) | 265 of 568 (47%); fingerprint `939|175|0|0|9|930|1` |
| 3 | that fingerprint in January | none | 0 |
| 3 | mean finetune_k8 score (missed reports of that fingerprint) | 0.997 | 0.9971 |
| 4 | 1% FPR threshold finetune_k8 / frozen_k1 | 0.99896 / 0.8745 | 0.99896 / 0.8745 |
| 4 | April benign scoring > 0.9, finetune_k8 / frozen_k1 | 675 / 73 | 675 / 73 |
| 4 | API calls of the 20 highest-scoring benign reports | 1 to 13 | 1 to 219 |
| 5 | fingerprints with both labels / reports / median API calls | 609 / 21,215 / 12 | 609 / 21,215 / 12 |
| 5 | April malware in such groups | 26.5% | 26.5% |
| 5 | finetune_k8 misses in such groups | 33.5% | 33.5% |

## 2. Exact duplicates and label conflicts (task 1)

Exact hash = SHA-1 of Nebula's filtered report (`filter_and_normalize_report()` output) serialised with sorted keys. Second check: SHA-1 of the API-name sequence only. Groups are over all 92,700 reports.

| grouping | groups | reports with a duplicate in the same split | April reports with a duplicate in January | groups with both labels | reports in those groups | median API calls in those groups | April malware in those groups | finetune_k8 misses in those groups |
|---|---|---|---|---|---|---|---|---|
| filtered report | 74,925 | 21.1% (19,527) | 6.8% (1,192) | 45 | 1.7% (1,545) | 10 | 1.7% (159) | 6.3% (151) |
| API-name sequence | 8,643 | 93.8% (86,925) | 36.4% (6,329) | 194 | 15.2% (14,117) | 188 | 27.3% (2,564) | 29.3% (697) |
| coarse fingerprint (preliminary) | 14,579 | 89.5% (82,968) | 32.1% (5,582) | 609 | 22.9% (21,215) | 12 | 26.5% (2,490) | 33.5% (797) |

Families of the reports in exact-hash groups with both labels (all splits):

| family     |   testset |   trainset |   all |
|:-----------|----------:|-----------:|------:|
| clean      |       293 |        481 |   774 |
| coinminer  |        38 |        313 |   351 |
| dropper    |        13 |        217 |   230 |
| ransomware |        82 |         35 |   117 |
| keylogger  |        10 |         31 |    41 |
| trojan     |         8 |         15 |    23 |
| rat        |         7 |          0 |     7 |
| backdoor   |         1 |          1 |     2 |

Exact-hash groups with both labels: 45; size median 10, max 321; API calls per report in them: median 10, p90 242.

Largest exact-hash groups with both labels:

| hash_report | size | malware | benign | calls | API names (first 6) |
|---|---|---|---|---|---|
| 8b15f05bba | 321 | 320 | 1 | 242 | SetErrorMode, GetVersion, GetModuleHandleA, GetProcAddress, SetDefaultDllDirectories, GetSystemDirectoryW |
| 638451c38d | 187 | 25 | 162 | 10 | GetModuleHandleA, GetCommandLineA, GetModuleHandleA, GetVersion, GetProcAddress, SetDefaultDllDirectories |
| b3a8e94c70 | 152 | 151 | 1 | 7 | __set_app_type, __p__fmode, __p__commode, _controlfp, _initterm, __wgetmainargs |
| de665fd57f | 131 | 82 | 49 | 55 | SetErrorMode, GetVersion, GetModuleHandleA, GetProcAddress, SetDefaultDllDirectories, GetSystemDirectoryW |
| 6469d90962 | 129 | 6 | 123 | 9 | GetModuleHandleA, GetCommandLineA, GetModuleHandleA, GetProcAddress, SetDllDirectoryW, GetProcAddress |
| ca22dbf32e | 91 | 13 | 78 | 7 | GetModuleHandleA, GetCommandLineA, GetModuleHandleA, GetVersion, GetProcAddress, SetDefaultDllDirectories |
| 568755fa31 | 82 | 5 | 77 | 6 | GetModuleHandleA, GetCommandLineA, GetModuleHandleA, GetProcAddress, SetDllDirectoryW, GetProcAddress |
| b7a11b32b2 | 60 | 8 | 52 | 3 | LoadLibraryA, GetProcAddress, ExitProcess |
| cc478ff6e9 | 38 | 35 | 3 | 238 | SetErrorMode, GetVersion, GetModuleHandleA, GetProcAddress, SetDefaultDllDirectories, GetSystemDirectoryA |
| f1f54492bd | 31 | 19 | 12 | 192 | ordinal_17, SetErrorMode, OleInitialize, GetModuleHandleA, LoadLibraryA, SHGetFileInfoA |

Largest API-name-sequence groups with both labels (194 groups, 14,117 reports; groups where one label is ≥ 99% of the reports: 9, holding 40.5% (5,722) of their reports):

| hash_apis | size | malware | benign | calls | families | first API names |
|---|---|---|---|---|---|---|
| c271f36a4b | 2292 | 2288 | 4 | 225 | keylogger 1,063, rat 665, coinminer 558 | GetSystemTimeAsFileTime, GetCurrentThreadId, GetCurrentProcessId, QueryPerformanceCounter, GetStartupInfoW, GetProcessHeap |
| 0fcca0c42a | 1098 | 1095 | 3 | 231 | keylogger 1,095, clean 3 | GetModuleHandleW, InitializeCriticalSection, InitializeCriticalSection, GetVersion, GetModuleHandleW, GetProcAddress |
| 5884e65612 | 864 | 862 | 2 | 219 | rat 549, coinminer 277, keylogger 36 | GetSystemTimeAsFileTime, GetCurrentThreadId, GetCurrentProcessId, QueryPerformanceCounter, GetStartupInfoW, GetProcessHeap |
| 9947cd115e | 634 | 623 | 11 | 500 | coinminer 620, clean 11, keylogger 3 | GetSystemTimeAsFileTime, GetCurrentProcessId, GetCurrentThreadId, GetTickCount, QueryPerformanceCounter, GetStartupInfoA |
| 0e9c897007 | 614 | 611 | 3 | 32 | keylogger 611, clean 3 | GetModuleHandleW, InitializeCriticalSection, InitializeCriticalSection, GetVersion, GetModuleHandleW, GetProcAddress |
| 7038a53a8f | 512 | 176 | 336 | 33 | clean 336, trojan 173, coinminer 1 | GetModuleHandleW, SetThreadLocale, InitializeCriticalSection, GetVersion, GetModuleHandleW, GetProcAddress |
| 1b5f31db73 | 511 | 221 | 290 | 10 | clean 290, keylogger 220, backdoor 1 | GetSystemTimeAsFileTime, GetCurrentProcessId, GetCurrentThreadId, GetTickCount, QueryPerformanceCounter, GetStartupInfoA |
| 941998dd87 | 500 | 333 | 167 | 242 | coinminer 217, clean 167, dropper 69 | SetErrorMode, GetVersion, GetModuleHandleA, GetProcAddress, SetDefaultDllDirectories, GetSystemDirectoryW |
| d8bc798838 | 411 | 247 | 164 | 16 | keylogger 238, clean 164, coinminer 7 | GetModuleHandleW, GetSystemInfo, GetKeyboardType, GetCommandLineW, GetStartupInfoA, GetACP |
| 9b55df4641 | 380 | 133 | 247 | 5 | clean 247, dropper 61, trojan 39 | __set_app_type, SetUnhandledExceptionFilter, __getmainargs, __p__fmode, __p__environ |
| 26af352f43 | 267 | 232 | 35 | 192 | coinminer 218, clean 35, dropper 5 | ordinal_17, SetErrorMode, OleInitialize, GetModuleHandleA, LoadLibraryA, SHGetFileInfoA |
| 0459938b31 | 252 | 10 | 242 | 11 | clean 242, dropper 8, rat 1 | GetSystemTimeAsFileTime, GetCurrentProcessId, GetCurrentThreadId, GetTickCount, QueryPerformanceCounter, GetStartupInfoW |

## 3. Why emulation stopped (task 2)

Stop reason of a report = `error.type` of its first entry point (the module entry), grouped into categories; raw types are in the second table. "No error recorded" means the entry point returned (or ended without an error record).

| April group (finetune_k8) | n | no error recorded | invalid memory / CPU fault | max_api_count (500-call cap) | unsupported API | emulator internal error |
|---|---|---|---|---|---|---|
| ransomware missed | 846 | 38.8% (328) | 1.3% (11) | 3.9% (33) | 54.5% (461) | 1.5% (13) |
| ransomware caught | 1,293 | 36.0% (466) | 4.3% (55) | 10.2% (132) | 49.5% (640) | 0.0% (0) |
| coinminer missed | 568 | 45.1% (256) | 34.0% (193) | 3.0% (17) | 17.3% (98) | 0.7% (4) |
| coinminer caught | 1,116 | 11.6% (129) | 6.4% (71) | 2.5% (28) | 79.6% (888) | 0.0% (0) |

Most common raw error types (module entry), April ransomware and coinminer:

| group | n | top error types |
|---|---|---|
| ransomware missed | 846 | `unsupported_api` 54.5% (461); `none` 38.8% (328); `max_api_count` 3.9% (33); `Unsupported information class: 0x0` 1.4% (12) |
| ransomware caught | 1,293 | `unsupported_api` 49.5% (640); `none` 36.0% (466); `max_api_count` 10.2% (132); `invalid_read` 2.3% (30) |
| coinminer missed | 568 | `none` 45.1% (256); `invalid_read` 31.9% (181); `unsupported_api` 17.3% (98); `max_api_count` 3.0% (17) |
| coinminer caught | 1,116 | `unsupported_api` 79.6% (888); `none` 11.6% (129); `Invalid memory read (UC_ERR_READ_UNMAPPED)` 5.5% (61); `max_api_count` 2.5% (28) |

Unsupported API names (any entry point), April ransomware and coinminer:

| group | reports with an unsupported API | top unsupported APIs |
|---|---|---|
| ransomware missed | 54.6% (462) | `KERNEL32.HeapValidate` (255); `shlwapi.ordinal_437` (80); `gdi32.GetSystemPaletteEntries` (43); `MSVCR80.setlocale` (39); `USER32.GetShellWindow` (9) |
| ransomware caught | 83.0% (1,073) | `msvcrt.__p___initenv` (478); `iphlpapi.GetAdaptersInfo` (407); `KERNEL32.HeapValidate` (100); `USER32.SetMenuInfo` (43); `PSAPI.EnumDeviceDrivers` (26) |
| coinminer missed | 18.3% (104) | `COMCTL32.ordinal_17` (16); `kernel32.SetSearchPathMode` (15); `KERNEL32.GetProcessAffinityMask` (12); `USER32.RegisterClipboardFormatA` (8); `KERNEL32.OpenFileMappingA` (7) |
| coinminer caught | 80.4% (897) | `KERNEL32.GetProcessAffinityMask` (560); `USER32.MapVirtualKeyW` (278); `imagehlp.ImageDirectoryEntryToData` (29); `ADVAPI32.RegCreateKeyExA` (6); `kernel32.FreeResource` (5) |

Stop reason per family, January (trainset) vs April (testset):

| family | split | n | no error recorded | invalid memory / CPU fault | max_api_count (500-call cap) | unsupported API | emulator internal error |
|---|---|---|---|---|---|---|---|
| backdoor | Jan | 11,061 | 30.8% (3,404) | 1.1% (125) | 67.9% (7,512) | 0.0% (0) | 0.2% (20) |
| backdoor | Apr | 1,940 | 23.7% (460) | 0.6% (12) | 59.5% (1,154) | 14.4% (279) | 1.8% (35) |
| clean | Jan | 24,433 | 51.8% (12,653) | 38.6% (9,430) | 9.0% (2,209) | 0.0% (0) | 0.6% (141) |
| clean | Apr | 7,944 | 32.5% (2,584) | 6.1% (482) | 8.4% (670) | 51.9% (4,121) | 1.1% (87) |
| coinminer | Jan | 6,891 | 28.5% (1,965) | 41.3% (2,846) | 29.5% (2,033) | 0.0% (0) | 0.7% (47) |
| coinminer | Apr | 1,684 | 22.9% (385) | 15.7% (264) | 2.7% (45) | 58.6% (986) | 0.2% (4) |
| dropper | Jan | 8,243 | 52.9% (4,363) | 40.5% (3,342) | 3.1% (256) | 0.0% (0) | 3.4% (282) |
| dropper | Apr | 252 | 37.3% (94) | 28.6% (72) | 3.2% (8) | 28.6% (72) | 2.4% (6) |
| keylogger | Jan | 4,378 | 16.3% (714) | 82.6% (3,617) | 1.0% (43) | 0.0% (0) | 0.1% (4) |
| keylogger | Apr | 1,041 | 19.4% (202) | 4.1% (43) | 0.6% (6) | 75.9% (790) | 0.0% (0) |
| ransomware | Jan | 9,627 | 74.1% (7,137) | 20.8% (1,999) | 5.1% (488) | 0.0% (0) | 0.0% (3) |
| ransomware | Apr | 2,139 | 37.1% (794) | 3.1% (66) | 7.7% (165) | 51.5% (1,101) | 0.6% (13) |
| rat | Jan | 1,697 | 14.7% (249) | 84.0% (1,425) | 1.0% (17) | 0.0% (0) | 0.4% (6) |
| rat | Apr | 1,258 | 22.2% (279) | 1.9% (24) | 0.8% (10) | 74.2% (933) | 1.0% (12) |
| trojan | Jan | 8,733 | 37.2% (3,251) | 37.3% (3,260) | 25.1% (2,191) | 0.0% (0) | 0.4% (31) |
| trojan | Apr | 1,085 | 25.5% (277) | 9.1% (99) | 2.0% (22) | 62.9% (683) | 0.4% (4) |
| windows_syswow64 | Jan | 235 | 9.8% (23) | 0.9% (2) | 0.0% (0) | 89.4% (210) | 0.0% (0) |
| windows_syswow64 | Apr | 59 | 13.6% (8) | 0.0% (0) | 0.0% (0) | 86.4% (51) | 0.0% (0) |

## 4. What the missed ransomware does (task 3)

Missed/caught = `finetune_k8` at 1% FPR. Shares are of the reports in each group.

| group | n | median API calls | file_access | registry_access | network traffic | >1 entry point | raw `process_events` | raw `dropped_files` | raw `dynamic_code_segments` | raw `handled_exceptions` |
|---|---|---|---|---|---|---|---|---|---|---|
| Apr missed | 846 | 142 | 1.4% (12) | 5.6% (47) | 0.4% (3) | 0.1% (1) | 0.2% (2) | 0.0% (0) | 0.0% (0) | 0.5% (4) |
| Apr caught | 1,293 | 142 | 36.3% (469) | 3.6% (46) | 31.8% (411) | 33.6% (434) | 0.0% (0) | 0.0% (0) | 0.2% (2) | 0.2% (3) |
| Jan (all) | 9,627 | 180 | 3.1% (302) | 0.8% (75) | 2.6% (246) | 3.0% (285) | 0.1% (9) | 0.1% (6) | 0.1% (10) | 4.0% (385) |

File-encryption related APIs (share of reports that call it at least once):

| API | Apr missed | Apr caught | Jan (all) |
|---|---|---|---|
| `CryptEncrypt` | 0.0% (0) | 0.0% (0) | 0.0% (0) |
| `CryptAcquireContext*` | 0.2% (2) | 31.6% (409) | 3.0% (284) |
| `BCrypt*` | 0.0% (0) | 0.0% (0) | 0.0% (1) |
| `FindFirstFile*` | 0.0% (0) | 0.0% (0) | 0.0% (0) |
| `FindNextFile*` | 0.0% (0) | 0.0% (0) | 0.0% (0) |
| `CreateFile*` | 1.4% (12) | 36.3% (469) | 3.1% (302) |
| `WriteFile` | 0.2% (2) | 0.0% (0) | 0.1% (6) |
| `MoveFile*` | 0.0% (0) | 0.0% (0) | 0.0% (0) |
| `DeleteFile*` | 0.0% (0) | 0.0% (0) | 0.0% (0) |
| `any FindFirst/FindNext + Write/Move` | 0.0% (0) | 0.0% (0) | 0.0% (0) |

Anti-analysis or delay APIs:

| API | Apr missed | Apr caught | Jan (all) |
|---|---|---|---|
| `IsDebuggerPresent` | 0.0% (0) | 0.0% (0) | 0.0% (0) |
| `CheckRemoteDebuggerPresent` | 0.0% (0) | 0.0% (0) | 0.0% (0) |
| `GetTickCount*` | 77.1% (652) | 41.1% (532) | 7.8% (753) |
| `QueryPerformanceCounter` | 78.7% (666) | 18.9% (244) | 7.6% (728) |
| `Sleep*` | 0.1% (1) | 33.5% (433) | 2.9% (279) |
| `GetSystemMetrics` | 0.9% (8) | 0.0% (0) | 0.0% (3) |
| `GetCursorPos` | 0.7% (6) | 0.0% (0) | 0.0% (2) |

Top 15 API names by document frequency (lower-case, without DLL):

| group | top APIs |
|---|---|
| Apr missed | `getprocaddress` 93%; `getcurrentthreadid` 85%; `queryperformancecounter` 79%; `getcurrentprocessid` 78%; `getsystemtimeasfiletime` 78%; `gettickcount` 77%; `heapalloc` 76%; `interlockedincrement` 76%; `getstdhandle` 74%; `getenvironmentstringsw` 74%; `getfiletype` 74%; `freeenvironmentstringsw` 74%; `entercriticalsection` 74%; `leavecriticalsection` 74%; `flsalloc` 74% |
| Apr caught | `_controlfp` 75%; `__p__fmode` 75%; `__p__commode` 75%; `__set_app_type` 75%; `__getmainargs` 75%; `_initterm` 75%; `getstartupinfoa` 47%; `getmodulefilenamea` 42%; `gettickcount` 41%; `getmodulehandlea` 39%; `__setusermatherr` 37%; `readfile` 36%; `closehandle` 33%; `sleep` 33%; `__p___argc` 33% |
| Jan (all) | `getprocaddress` 54%; `getvolumeinformation` 46%; `getversionex` 46%; `virtualalloc` 46%; `loadlibrarya` 46%; `getenvironmentvariablew` 45%; `localalloc` 45%; `initializesecuritydescriptor` 45%; `setsecuritydescriptordacl` 45%; `getcurrentthreadid` 9%; `getcurrentprocessid` 9%; `getlasterror` 9%; `getstartupinfoa` 8%; `getmodulehandlew` 8%; `gettickcount` 8% |

APIs whose document frequency differs most, Apr missed (n=846) vs Apr caught (n=1,293); log-odds with +0.5 smoothing, APIs in ≥20 reports:

| direction | API | Apr missed | Apr caught | log-odds |
|---|---|---|---|---|
| more in Apr missed | `loadlibraryw` | 31.1% (263) | 0.1% (1) | +5.96 |
| more in Apr missed | `getsystemdirectoryw` | 9.5% (80) | 0.0% (0) | +5.60 |
| more in Apr missed | `heapsetinformation` | 29.8% (252) | 0.2% (2) | +5.39 |
| more in Apr missed | `getversionexa` | 6.4% (54) | 0.0% (0) | +5.18 |
| more in Apr missed | `localalloc` | 6.1% (52) | 0.0% (0) | +5.14 |
| more in Apr missed | `createeventa` | 6.0% (51) | 0.0% (0) | +5.12 |
| more in Apr missed | `regopenkeyexa` | 5.6% (47) | 0.0% (0) | +5.03 |
| more in Apr missed | `lstrcpyna` | 5.6% (47) | 0.0% (0) | +5.03 |
| more in Apr missed | `loadstringa` | 5.6% (47) | 0.0% (0) | +5.03 |
| more in Apr missed | `getlocaleinfoa` | 5.6% (47) | 0.0% (0) | +5.03 |
| more in Apr caught | `__getmainargs` | 0.2% (2) | 75.3% (974) | -6.94 |
| more in Apr caught | `_controlfp` | 0.2% (2) | 75.3% (974) | -6.94 |
| more in Apr caught | `__setusermatherr` | 0.0% (0) | 37.1% (480) | -6.91 |
| more in Apr caught | `__p__commode` | 0.4% (3) | 75.3% (974) | -6.60 |
| more in Apr caught | `__p__fmode` | 0.4% (3) | 75.3% (974) | -6.60 |
| more in Apr caught | `__set_app_type` | 0.4% (3) | 75.3% (974) | -6.60 |
| more in Apr caught | `readfile` | 0.1% (1) | 36.2% (468) | -5.77 |
| more in Apr caught | `sleep` | 0.1% (1) | 33.5% (433) | -5.65 |
| more in Apr caught | `__p___argc` | 0.1% (1) | 33.1% (428) | -5.63 |
| more in Apr caught | `exit` | 0.1% (1) | 31.8% (411) | -5.57 |

APIs whose document frequency differs most, Apr missed (n=846) vs Jan (all) (n=9,627); log-odds with +0.5 smoothing, APIs in ≥20 reports:

| direction | API | Apr missed | Jan (all) | log-odds |
|---|---|---|---|---|
| more in Apr missed | `loadlibraryw` | 31.1% (263) | 0.2% (16) | +5.57 |
| more in Apr missed | `heapsetinformation` | 29.8% (252) | 0.2% (22) | +5.20 |
| more in Apr missed | `interlockedexchange` | 4.6% (39) | 0.1% (6) | +4.28 |
| more in Apr missed | `interlockedcompareexchange` | 4.6% (39) | 0.1% (6) | +4.28 |
| more in Apr missed | `_initterm_e` | 4.6% (39) | 0.1% (7) | +4.14 |
| more in Apr missed | `interlockedincrement` | 76.1% (644) | 5.4% (519) | +4.02 |
| more in Apr missed | `getcurrentthreadid` | 84.8% (717) | 9.3% (898) | +3.99 |
| more in Apr missed | `tlssetvalue` | 71.9% (608) | 5.1% (493) | +3.85 |
| more in Apr missed | `heapcreate` | 71.9% (608) | 5.1% (493) | +3.85 |
| more in Apr missed | `initializecriticalsectionandspincount` | 72.7% (615) | 5.3% (513) | +3.85 |
| more in Jan (all) | `getversionex` | 0.0% (0) | 46.5% (4,476) | -7.29 |
| more in Jan (all) | `getvolumeinformation` | 0.0% (0) | 46.5% (4,476) | -7.29 |
| more in Jan (all) | `initializesecuritydescriptor` | 0.0% (0) | 45.2% (4,349) | -7.24 |
| more in Jan (all) | `setsecuritydescriptordacl` | 0.0% (0) | 45.1% (4,345) | -7.24 |
| more in Jan (all) | `getenvironmentvariablew` | 0.1% (1) | 45.5% (4,379) | -6.15 |
| more in Jan (all) | `getconsolewindow` | 0.0% (0) | 6.0% (582) | -4.69 |
| more in Jan (all) | `getadaptersinfo` | 0.0% (0) | 2.5% (240) | -3.77 |
| more in Jan (all) | `getdoubleclicktime` | 0.0% (0) | 1.9% (184) | -3.50 |
| more in Jan (all) | `getmessageextrainfo` | 0.0% (0) | 1.7% (165) | -3.39 |
| more in Jan (all) | `getclipboardviewer` | 0.0% (0) | 1.6% (155) | -3.32 |

Most common last 5 API calls (endings), per group:

| group | last 5 calls | reports |
|---|---|---|
| Apr missed | `heapsize → encodepointer → encodepointer → leavecriticalsection → loadlibraryw` | 17.1% (145) |
| Apr missed | `heapalloc → leavecriticalsection → multibytetowidechar → getstringtypew → entercriticalsection` | 16.3% (138) |
| Apr missed | `leavecriticalsection → heapalloc → entercriticalsection → heapalloc → leavecriticalsection` | 13.8% (117) |
| Apr missed | `getlasterror → tlsgetvalue → flsgetvalue → setlasterror → loadlibraryw` | 11.9% (101) |
| Apr caught | `__setusermatherr → _controlfp → _initterm → __getmainargs → _initterm` | 37.0% (478) |
| Apr caught | `gettickcount → gettickcount → gettickcount → gettickcount → gettickcount` | 31.5% (407) |
| Apr caught | `leavecriticalsection → heapalloc → entercriticalsection → heapalloc → leavecriticalsection` | 4.8% (62) |
| Apr caught | `memcmp → memcmp → memcmp → memcmp → memcmp` | 4.7% (61) |
| Jan (all) | `virtualalloc → virtualalloc → virtualalloc → virtualalloc → getenvironmentvariablew` | 45.1% (4,345) |
| Jan (all) | `gettickcount → gettickcount → gettickcount → gettickcount → gettickcount` | 2.5% (241) |
| Jan (all) | `getuserdefaultuilanguage → getuserdefaultuilanguage` | 2.2% (215) |
| Jan (all) | `getconsolewindow → getconsolewindow` | 2.2% (208) |

Exact-hash structure of the missed ransomware: 746 distinct filtered reports among 846; the largest exact group holds 75; 9.7% (82) sit in a group that also has benign reports.

## 5. The big coinminer group (task 4)

Coinminer misses (`finetune_k8`): 568. Largest coarse fingerprint `939|175|0|0|9|930|1` (tokens|API calls|registry|network|file|apis tokens|entry points) holds 46.7% (265) of them.

- Distinct exact filtered-report hashes in that group: 1 (largest: 265 reports).
- Distinct API-name sequences: 1 (largest: 265).
- All April reports with that fingerprint: 265 ({'coinminer': np.int64(265)}); January reports with it: 0; January reports with the same exact filtered-report hash as the largest exact group: 0.
- `finetune_k8` on the whole fingerprint group: mean score 0.9971, median 0.9971, flagged 0.0% (0) (threshold 0.99896).
- `frozen_k1` on the whole fingerprint group: mean score 0.9991, median 0.9991, flagged 100.0% (265) (threshold 0.87452).

Closest January coinminer by edit distance over API-name sequences (lower-case; 257 distinct January coinminer sequences searched): `4bcbd50b4ede1e3716f4c8560050243d82583af1a074d024840cddf999ca84a1`, distance **14** (175 vs 178 calls; 1 reports share that January sequence).

Minimal edit script (14 edits; `delete` = only in April, `insert` = only in January), consecutive edits merged:

| edit | at April call | April calls | January calls |
|---|---|---|---|
| replace | 120 | loadlibrarya | getprocaddress |
| replace | 127 | loadlibrarya | getprocaddress |
| replace | 131 | loadlibrarya | getprocaddress |
| replace | 137 | loadlibrarya | getprocaddress |
| replace | 145 | loadlibrarya | getprocaddress |
| replace | 147 | loadlibrarya | getprocaddress |
| replace | 149 | loadlibrarya | getprocaddress |
| replace | 151 | loadlibrarya | getprocaddress |
| insert | 165 | – | loadlibrarya |
| insert | 172 | – | getprocaddress, getprocaddress |
| replace | 172 | virtualprotect, virtualprotect, createfilea | getprocaddress, getprocaddress, getprocaddress |

Last 6 calls: April `getprocaddress → getprocaddress → getprocaddress → virtualprotect → virtualprotect → createfilea`; January `getprocaddress → getprocaddress → getprocaddress → getprocaddress → getprocaddress → getprocaddress`.

The full API-name list of the April report is in [`coinminer_group_example.txt`](coinminer_group_example.txt); its whole filtered report is in [`coinminer_group_example_filtered.json`](coinminer_group_example_filtered.json). Its non-API fields: {"file_access": [{"event": "create", "path": "<drive>\\windows\\mshlpda32.dll"}]}

## 6. Score calibration (task 5)

| model | benign score > | April benign reports | median API calls | ≤10 API calls | median exact-group size | in a group with malware | same API-name sequence as some malware | median malware share of their group |
|---|---|---|---|---|---|---|---|---|
| finetune_k8 | 0.9 | 8.4% (675) | 359 | 9.5% (64) | 1 | 0.6% (4) | 11.7% (79) | 0.00 |
| finetune_k8 | 0.99 | 2.2% (176) | 42 | 30.1% (53) | 1 | 1.7% (3) | 35.2% (62) | 0.00 |
| finetune_k8 | 0.999 | 0.9% (76) | 10 | 52.6% (40) | 1 | 1.3% (1) | 47.4% (36) | 0.00 |
| frozen_k1 | 0.9 | 0.9% (73) | 40 | 39.7% (29) | 1 | 1.4% (1) | 31.5% (23) | 0.00 |
| frozen_k1 | 0.99 | 0.4% (33) | 9 | 57.6% (19) | 1 | 3.0% (1) | 36.4% (12) | 0.00 |
| frozen_k1 | 0.999 | 0.2% (16) | 6 | 75.0% (12) | 1 | 6.2% (1) | 31.2% (5) | 0.00 |

`finetune_k8`: highest test score 0.99953; 7,066 reports within 0.0005 of it (73 benign, 6,993 malware). The 1% FPR threshold 0.99896 is 0.00057 below the highest score.

`frozen_k1`: highest test score 0.99984; 5,041 reports within 0.0005 of it (13 benign, 5,028 malware). The 1% FPR threshold 0.87452 is 0.12532 below the highest score.

The 10 highest-scoring April benign reports (`finetune_k8`):

| family | finetune_k8 | frozen_k1 | API calls | exact group: malware / size | API-sequence group: malware / size | API names |
|---|---|---|---|---|---|---|
| clean | 0.99951 | 0.9998 | 219 | 0 / 1 | 862 / 864 | GetSystemTimeAsFileTime, GetCurrentThreadId, GetCurrentProcessId, QueryPerformanceCounter, GetStartupInfoW, GetProcessHeap, EncodePointer, EncodePointer |
| clean | 0.99951 | 0.9994 | 219 | 0 / 1 | 862 / 864 | GetSystemTimeAsFileTime, GetCurrentThreadId, GetCurrentProcessId, QueryPerformanceCounter, GetStartupInfoW, GetProcessHeap, EncodePointer, EncodePointer |
| clean | 0.99948 | 0.9998 | 47 | 0 / 1 | 0 / 1 | GetCommandLineA, GetVersionExA, InitializeCriticalSection, EnterCriticalSection, GetProcessHeap, GetSystemTimeAsFileTime, GetCurrentProcessId, GetCurrentThreadId |
| clean | 0.99947 | 0.9966 | 48 | 0 / 1 | 0 / 1 | GetVersion, HeapCreate, HeapAlloc, HeapAlloc, VirtualAlloc, VirtualAlloc, GetStartupInfoA, GetStdHandle |
| clean | 0.99947 | 0.0698 | 9 | 0 / 1 | 72 / 119 | __set_app_type, __p__fmode, __p__commode, _controlfp, _initterm, __getmainargs, _initterm, GetStartupInfoA |
| clean | 0.99947 | 0.9998 | 7 | 0 / 1 | 10 / 28 | __set_app_type, __p__fmode, __p__commode, _controlfp, _initterm, __getmainargs, _initterm |
| clean | 0.99947 | 0.4432 | 9 | 0 / 1 | 72 / 119 | __set_app_type, __p__fmode, __p__commode, _controlfp, _initterm, __getmainargs, _initterm, GetStartupInfoA |
| clean | 0.99947 | 0.9975 | 9 | 0 / 1 | 72 / 119 | __set_app_type, __p__fmode, __p__commode, _controlfp, _initterm, __getmainargs, _initterm, GetStartupInfoA |
| clean | 0.99946 | 0.9983 | 7 | 0 / 1 | 10 / 28 | __set_app_type, __p__fmode, __p__commode, _controlfp, _initterm, __getmainargs, _initterm |
| clean | 0.99946 | 0.9998 | 1 | 0 / 1 | 0 / 3 | LoadLibraryA |

## 7. Effect of removing unlearnable reports (task 6, analysis only)

TPR per family at 1% FPR, with the threshold recomputed on the April benign reports that remain. (a) removes every April report in an exact-hash group that contains both labels (groups over all splits); (b) removes reports with 10 or fewer API calls; (a+b) both.

| subset | benign kept | malware kept | model | all malware | ransomware | coinminer | backdoor | dropper | keylogger | rat | trojan |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 8,003 | 9,399 | finetune_k8 | 74.7% (7,018) | 60.4% (1,293/2,139) | 66.3% (1,116/1,684) | 80.0% (1,552/1,940) | 77.4% (195/252) | 88.1% (917/1,041) | 84.8% (1,067/1,258) | 80.9% (878/1,085) |
| all | 8,003 | 9,399 | frozen_k1 | 75.8% (7,129) | 66.5% (1,422/2,139) | 79.5% (1,339/1,684) | 82.2% (1,595/1,940) | 71.8% (181/252) | 64.4% (670/1,041) | 83.9% (1,056/1,258) | 79.8% (866/1,085) |
| (a) no label-conflict groups | 7,710 | 9,240 | finetune_k8 | 75.8% (7,005) | 62.7% (1,289/2,057) | 67.8% (1,116/1,646) | 80.0% (1,552/1,939) | 78.2% (187/239) | 88.8% (916/1,031) | 85.3% (1,067/1,251) | 81.5% (878/1,077) |
| (a) no label-conflict groups | 7,710 | 9,240 | frozen_k1 | 77.0% (7,113) | 68.8% (1,416/2,057) | 81.3% (1,339/1,646) | 82.3% (1,595/1,939) | 72.4% (173/239) | 65.0% (670/1,031) | 84.3% (1,055/1,251) | 80.3% (865/1,077) |
| (b) > 10 API calls | 6,486 | 8,266 | finetune_k8 | 76.8% (6,347) | 54.3% (854/1,573) | 69.7% (1,139/1,635) | 83.5% (1,523/1,825) | 77.3% (143/185) | 89.9% (830/923) | 89.7% (1,064/1,186) | 84.6% (794/939) |
| (b) > 10 API calls | 6,486 | 8,266 | frozen_k1 | 79.0% (6,533) | 61.7% (971/1,573) | 83.2% (1,360/1,635) | 83.1% (1,516/1,825) | 70.8% (131/185) | 74.2% (685/923) | 90.8% (1,077/1,186) | 84.5% (793/939) |
| (a+b) | 6,403 | 8,145 | finetune_k8 | 77.9% (6,347) | 57.3% (854/1,491) | 70.6% (1,139/1,614) | 83.5% (1,523/1,825) | 79.4% (143/180) | 90.6% (830/916) | 90.2% (1,064/1,180) | 84.6% (794/939) |
| (a+b) | 6,403 | 8,145 | frozen_k1 | 80.2% (6,533) | 65.1% (971/1,491) | 84.3% (1,360/1,614) | 83.1% (1,516/1,825) | 72.8% (131/180) | 74.8% (685/916) | 91.3% (1,077/1,180) | 84.5% (793/939) |
