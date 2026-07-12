Given a rule {rule} that defines the shape and/or quality of an artitfact
    and that rule has a associated scanner {scanner} that can mechanically checks compliace to the rule.
    and an output file {passing_output} that is consistent with the rule and the scanner
    and an output file {failing output} is not consistent with rule and not supportef by the scanner

when the output file {passing_output} is validated by the rule {rule}
then the rule validation will pass
and the scanner {scanner} scan will pass


when the output file {failing_output} is validated by the rule {rule}
then the rule validation will fail
and the scanner {scanner} scan will also fail




 

