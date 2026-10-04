class Structure:
    type_1 = {
        1: "$keyword",
        2: "$value:datatype",
        3: "$block"
    }
    type_2 = {
        1: "$keyword",
        2: "$value:datatype",
        3: "$helper",
        4: "$value:datatype"
    }
    type_3 = {
        0: "$previous",
        1: "$keyword",
        2: "$value:datatype",
        3: "$block"
    }
    type_4 = {
        0: "$previous",
        1: "$keyword",
        3: "$block"
    }
    def parse(self, comps, k_type):
        key = comps.pop(0)
