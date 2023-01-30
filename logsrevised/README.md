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
