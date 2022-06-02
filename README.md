# hldiscovery

Here you can find algorithm implementation as a set of __PM4Py__ using modules.

In this repository, there are implementation of our algorithm and the results of the qualitative experimental evaluation of it.
In the tests folder, there are initial raw logs for the large model from the paper and resulting logs and Petri nets in the __final_logs*__ and __final_nets*__ folders respectively.

To check the conformance of resulting logs with an initially created model (with domain knowledge of an expert) we need to replay the resulting traces on the model. For each trace, four values have to be determined: **p**roduced tokens, **r**emaining tokens, **m**issing tokens, and **c**onsumed tokens. Based on that, a formula can be derived, whereby a Petri net N and a trace σ are given as input:

$$ fitness(σ,N) = 1/2*(1-m/c)+1/2*(1-r/p) $$

So in our case with cycles, the value of the fitness indicator is directly related to the coverability of the initial logs, for small logs - the coverage of possible model behavior is quite limited, which directly affects the ability of the algorithm to correctly extract information about cycles.

For conducting experiments the Inductive Miner discovery algorithm was used to extract the causality and concurrent relations from initial logs. It is important to know that Inductive Miner has some limitations in this aspect, so the quality of relations is connected with the log coverability.

After relations extraction, from every log, were extracted cycles via our implementation of an algorithm to that we have the reference in our main paper. Then we apply our log preprocessing algorithm6 using information about the log's cycles. After that we check conformance between the resulting log and the initial high-level process model, that was constructed by us to define the initial mapping of abstract events to a detailed one. The net and the mapping you can also find here  (**hlpetrinet.pnml** and ***mapping.json** respectively).

For 90 initial logs (10 traces in each) from the  **initial_logs** folder the fitness measures are next:

1.0; 0.8554464285714286; 0.9373861885418127; 0.7518122247158647; 0.9048654365965448; 0.7367879136897237; 0.7691866040587554; 0.8696507624200689; 0.9601142615319509; 0.8893280632411067; 0.8573846573846574; 1.0; 0.9146612435506346; 0.7969617680477539; 0.8548172757475083; 0.8067978533094813; 0.831077694235589; 0.7994834988242058; 1.0; 0.7795775314956901; 1.0; 0.9003159358018451; 0.7518948373156559; 0.9344332855093256; 0.8687836553690211; 0.8167950693374422; 0.8052198092520673; 0.790516152189519; 0.9373511367737279; 0.9022029065489331; 0.9359340659340659; 1.0; 1.0; 0.8828231292517006; 0.9063841573189308; 0.7826257728379533; 0.9079595540575577; 0.9019810508182602; 0.8132961675924342; 0.7849556234540958; 0.7378193632757587; 0.8126743256158693; 0.8556769281694803; 0.8502909039307507; 0.7206760707593037; 0.8199912701876909; 0.8629239766081871; 0.8962452453583399; 0.8617363608005385; 0.758680587204149; 0.82557781201849; 0.8480281578004538; 0.980857310628303; 0.8212370005473453; 0.7809412721729396; 0.7941427076209225; 0.8795955882352942; 0.769164924967805; 0.7751168661365847; 0.7323750962942823; 0.751033342838001; 0.7737558193357181; 0.8104331625523986; 0.8962738219398881; 0.8056078767123288; 0.8389304812834224; 0.6651124989503543; 0.8085330059549009; 0.794975200482084; 0.8123154667272314; 0.9408158158158157; 0.9068228442856198; 0.8113204038677617; 0.9063841573189308; 0.9066141336239417; 0.9019810508182602; 1.0; 1.0; 0.9571895424836601; 0.8946078431372549; 0.854616523434679; 0.779826585248101; 0.827458520259204; 0.8475575662074926; 0.9580191050779285; 0.7988533205924511; 0.8416777926123721; 0.7770379220262019; 0.8281481481481481; 0.8760774040899104; 0.7952548485759242; 0.9094911937377691; 0.9125371089289792

For 10 initial logs (20 traces in each) from the **initial logs** folder the fitness measures are next:

0.8842167189601076; 0.6758961385317059; 0.792425296843559; 0.8622685185185186; 0.8467981760507534; 0.8374754558204769; 0.7645106832650326; 0.8332531500572737; 0.8879078134418324; 0.8229104436000988; 0.8842167189601076

For 10 initial logs (50 traces in each) from the **initial logs** folder the fitness measures are next:

0.74472110525879; 0.8157848188713016; 0.7763157195675325; 0.7950577625727515; 0.7816941897697016; 0.8254199339250885; 0.8102651984797757; 0.759417449546046; 0.8011547694476917; 0.7200086959480079; 0.74472110525879

For 10 initial logs (100 traces in each) from the **initial logs** folder the fitness measures are next:

0.8370493071300203; 0.8664917343999967; 0.7848158220796175; 0.7458534496143604; 0.852225680185974; 0.7453041783621255; 0.7590632741132713; 0.8090808855661855; 0.7739714733283866; 0.7930503925201698; 0.8370493071300203

For all of the initial logs was used the same parameter as steps maximum (100 steps). If we revise the resulting Petri nets (in **final_nets** folders for all parameters) and look at the output data in the file **console_output.txt** - we will see in detail which transitions were problematic in every case. There are also timing evaluations and in the average case, the time is compared with the usual inductive miner working time for the detailed log. However, there is a class of logs with cycles that could lead to complexity growing because of the increased number of possible combinations of high-level event log variations.

In the future, it could be interesting to find the optimal characteristics of generated logs or to find out another way how to define cycles even more precise way, than it was in this work. Also, it is necessary to define a class of logs with bigger time complexity to find out the way of algorithm optimization.
