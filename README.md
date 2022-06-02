# hldiscovery

Here you can find algorithm implementation as a set of __PM4Py__ using modules.

In **tests** folder there are initial raw logs for the large model from the paper and resulting logs and Petri nets in **final logs** and **final nets** folders respectively.

The value of the *fitness* indicator is directly related to the coverage of the initial logs, for small logs (95 logs of 10 traces were taken for the example) - the coverage of possible model behaviour is quite limited, which directly affects the ability of the algorithm to correctly extract information about cycles.
