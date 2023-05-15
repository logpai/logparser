Logparser

Logparser provides a toolkit and benchmarks for automated log parsing, which is a crucial step towards structured log analytics. By applying logparser, users can automatically learn event templates from unstructured logs and convert raw log messages into a sequence of structured events. In the literature, the process of log parsing is sometimes refered to as message template extraction, log key extraction, or log message clustering.

Dataset

The Logparser project provide sixteen widely-used datasets' logs and Ground Truth files.
![image](https://user-images.githubusercontent.com/24251293/215424237-30ef81df-d123-4d5b-8daf-bf0713a3c50d.png)

Errors

We thoroughly examined the current sixteen widely-used datasets' logs and Ground Truth files, and we discovered an amount of inaccuracies in those files. As a result, we decided to entirely and thoroughly modify the Ground Truth files.
Multiple errors in the current Ground Truth: (1) There are some strings that are misrepresented as arguments. (2) Poor consistency. Symbols are handled poorly; some are assigned as parameters while others are not. (3) Poor interpretability. Certain parameter settings are absurd. According to a set of rules, we modify the Ground Truth files. 

Modified rules

For the logs that can be confirmed by the source code, we alter the files in accordance with the source code. For other logs, we aim for consistency and common sense. If the guidelines are not applicable, we use our best judgment. To keep the consistency, the following regulations have been created. 
(1) Combining letters, integers, and symbols into a single parameter, if there is no space in between, symbols are not preserved. However, the symbol must be kept if there is a space between it and the character. Whatever the case, parentheses, square brackets, curly brackets, etc. need to be preserved. 
(2) The following are regarded as parameters: pure numbers, numbers only mixed with decimal points, and numbers only mixed with letters. 
(3) Strings with numerous decimal points between them are regarded as parameters (the number of decimal points is greater than 2). 
(4) It is treated as a parameter if it comes after the equal sign. 
(5) Under some circumstances, capital letters are parameters (e.g., from INITED to SETUP). 
(6) Paths and URLs are regarded as parameters. Whenever a string has more than two slashes, it is treated as a URL or path. 
(7) The use of certain special terms as parameters, such as null, true, and false. 
(8) Strings are treated as parameters if they follow certain specific terms, such as user and admin.

Present

![image](https://user-images.githubusercontent.com/24251293/215432750-f86c7c58-afe2-41a5-aab5-1840568dd896.png)

We have not made any changes for some particular circumstances or issues with the original data. After adjustment, the type and quantity of templates will change. We provide some details, such as how many template types have been edited, the number of original template types, and how many template types existed.

![image](https://user-images.githubusercontent.com/24251293/215428722-941099bc-799c-4f22-bbdd-d2b423b270f8.png)

Feedback

For any questions or feedback, please let us know.

More detraid information

Token
![image](https://github.com/logpai/logparser/assets/24251293/af5aabb6-673b-46fc-8ca0-2baee6a6594d)
![image](https://github.com/logpai/logparser/assets/24251293/bb3228a0-deaa-43cc-abc4-6dfb0612f2f9)
![image](https://github.com/logpai/logparser/assets/24251293/4435d5f0-eb6f-4bc9-abb5-6cb254d47729)
![image](https://github.com/logpai/logparser/assets/24251293/1f5e8d8f-04cf-4163-a0fa-e08717515d9a)
![image](https://github.com/logpai/logparser/assets/24251293/0b39680c-4f4f-4dc0-bb63-01987f16572b)
![image](https://github.com/logpai/logparser/assets/24251293/3e125ae0-9376-40b4-929c-b1f9ba95e65f)
![image](https://github.com/logpai/logparser/assets/24251293/b525ae4c-91d8-44cd-aafe-7be7a13a9216)

Parameter
![image](https://github.com/logpai/logparser/assets/24251293/83a90a70-3548-4ae2-97f6-4dd1a1866851)
![image](https://github.com/logpai/logparser/assets/24251293/4e2589d1-d6f7-4f62-b1d2-cbcd9ea14d7c)
![image](https://github.com/logpai/logparser/assets/24251293/d39bfe1a-7e67-4e63-9999-0e82f2b65942)
![image](https://github.com/logpai/logparser/assets/24251293/8a574ba3-3e00-4630-b6a5-54e385b63d0a)
![image](https://github.com/logpai/logparser/assets/24251293/4ab35e61-0a3c-4a65-9de5-431bcebacf2f)
![image](https://github.com/logpai/logparser/assets/24251293/14666aba-2265-4172-aa0c-9659b5d5d17b)
![image](https://github.com/logpai/logparser/assets/24251293/de7fb295-d671-42ce-9e98-84ad152a6ccf)

Avg Dis
![image](https://github.com/logpai/logparser/assets/24251293/3329664b-33ab-4a05-900a-0d740865143e)
![image](https://github.com/logpai/logparser/assets/24251293/e2ff4f65-7f5e-4eea-83c4-7c870d6f057e)
![image](https://github.com/logpai/logparser/assets/24251293/6913ba5c-3ed6-4da9-8fc0-8868d1485df6)
![image](https://github.com/logpai/logparser/assets/24251293/701f38f9-c5c9-4a3f-875d-2e595c5c36bf)
![image](https://github.com/logpai/logparser/assets/24251293/30326273-30c5-4a08-9f76-d670ce3136bc)
![image](https://github.com/logpai/logparser/assets/24251293/9ff02935-67ba-436a-97d6-695cacd28e08)
![image](https://github.com/logpai/logparser/assets/24251293/2d338d35-3b69-454e-b6c9-8177c1ad9b90)
![image](https://github.com/logpai/logparser/assets/24251293/0df80215-4b83-4386-86c3-9bbca8477139)

