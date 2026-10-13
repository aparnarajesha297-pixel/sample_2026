# Where the horizon gain comes from (row 15 diagnostic)

Run after the test results were seen, to explain them; not a selection step.

## H = 3, split by episode type (test)

| Evidence | Horizon | Episodes | n | F1 | Evidence cost | Total cost | Queries | Observations |
|---|---|---|---|---|---|---|---|---|
| a1-a4 | fixed H | first step of stream | 80105 | 0.9562 | 1.7140 | 3.0949 | 0.8709 | 1.4672 |
| a1-a4 | fixed H | later step | 43515 | 0.8626 | 0.7608 | 2.9182 | 0.3167 | 1.0754 |
| a1-a4 | fixed H | Sybil runs | 45234 | 0.9953 | 0.2719 | 0.4386 | 0.1318 | 1.0615 |
| a1-a4 | fixed H | other runs | 78386 | 0.8024 | 2.0170 | 4.5297 | 0.9898 | 1.4838 |
| a1-a4 | geometric cap | first step of stream | 80105 | 0.9835 | 1.9964 | 2.6955 | 0.5528 | 1.0000 |
| a1-a4 | geometric cap | later step | 43515 | 0.8684 | 0.7724 | 2.8871 | 0.3163 | 1.0725 |
| a1-a4 | geometric cap | Sybil runs | 45234 | 0.9979 | 0.2779 | 0.3521 | 0.0861 | 1.0044 |
| a1-a4 | geometric cap | other runs | 78386 | 0.8803 | 2.3086 | 4.1541 | 0.6908 | 1.0377 |
| a1 only | fixed H | first step of stream | 80105 | 0.9440 | 0.6943 | 3.2832 | 0.6943 | 1.6943 |
| a1 only | fixed H | later step | 43515 | 0.8505 | 0.2396 | 2.8277 | 0.2396 | 1.2396 |
| a1 only | fixed H | Sybil runs | 45234 | 0.9951 | 0.1033 | 0.2749 | 0.1033 | 1.1033 |
| a1 only | fixed H | other runs | 78386 | 0.7524 | 0.7829 | 4.7663 | 0.7829 | 1.7829 |
| a1 only | geometric cap | first step of stream | 80105 | 0.9440 | 0.6916 | 3.2860 | 0.6916 | 1.6916 |
| a1 only | geometric cap | later step | 43515 | 0.8504 | 0.2380 | 2.8302 | 0.2380 | 1.2380 |
| a1 only | geometric cap | Sybil runs | 45234 | 0.9951 | 0.1030 | 0.2746 | 0.1030 | 1.1030 |
| a1 only | geometric cap | other runs | 78386 | 0.7522 | 0.7795 | 4.7708 | 0.7795 | 1.7795 |

## Trivial rule vs the geometric cap (test)

Trivial rule: plan one step at a stream's first message, otherwise use the full horizon.

| Evidence | H | Horizon | F1 | Evidence cost | Total cost |
|---|---|---|---|---|---|
| a1-a4 | 2 | fixed H | 0.9442 | 1.3180 | 2.9458 |
| a1-a4 | 2 | geometric cap | 0.9683 | 1.5550 | 2.7416 |
| a1-a4 | 2 | trivial rule | 0.9684 | 1.5536 | 2.7633 |
| a1-a4 | 3 | fixed H | 0.9445 | 1.3785 | 3.0327 |
| a1-a4 | 3 | geometric cap | 0.9689 | 1.5655 | 2.7629 |
| a1-a4 | 3 | trivial rule | 0.9680 | 1.5621 | 2.7833 |
| a1-a4 | 5 | fixed H | 0.9435 | 1.4151 | 3.1200 |
| a1-a4 | 5 | geometric cap | 0.9686 | 1.5704 | 2.7757 |
| a1-a4 | 5 | trivial rule | 0.9682 | 1.5665 | 2.7880 |
| a1-a4 | 10 | fixed H | 0.9430 | 1.4438 | 3.1830 |
| a1-a4 | 10 | geometric cap | 0.9686 | 1.5775 | 2.7867 |
| a1-a4 | 10 | trivial rule | 0.9678 | 1.5710 | 2.8148 |
| a1 only | 2 | fixed H | 0.9273 | 0.4386 | 3.1230 |
| a1 only | 2 | geometric cap | 0.9273 | 0.4386 | 3.1230 |
| a1 only | 2 | trivial rule | 0.9273 | 0.4386 | 3.1230 |
| a1 only | 3 | fixed H | 0.9324 | 0.5343 | 3.1228 |
| a1 only | 3 | geometric cap | 0.9323 | 0.5320 | 3.1256 |
| a1 only | 3 | trivial rule | 0.9324 | 0.5325 | 3.1247 |
| a1 only | 5 | fixed H | 0.9405 | 0.7562 | 3.1369 |
| a1 only | 5 | geometric cap | 0.9405 | 0.7520 | 3.1435 |
| a1 only | 5 | trivial rule | 0.9405 | 0.7540 | 3.1391 |
| a1 only | 10 | fixed H | 0.9466 | 0.9362 | 3.1844 |
| a1 only | 10 | geometric cap | 0.9466 | 0.9273 | 3.1873 |
| a1 only | 10 | trivial rule | 0.9466 | 0.9339 | 3.1864 |
