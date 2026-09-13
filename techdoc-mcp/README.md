# techdoc-mcp

An AI-powered assistant that transforms functional requirements into structured technical proposal.

## Graph-Based definition

```
(:BusinessLine {id, code, name})
       ▲
       │  [:BELONGS_TO]
       │
   (:Family {id, name})
       ▲
       │  [:BELONGS_TO]
       │
(:ProductService {id, code, name, type, smbApplicable, corpApplicable, description})
       │
       │  [:REQUIRES_ROLE]  (Implicit modeling for business_line_role mappings)
       ▼
  (:HourlyRate {roleCode, category, position, level, smbRate, corporateRate, description})

(:Specialty {code, name, codeExample})
(:Surcharge {code, condition, factor, rule})
(:BlendedRate {id, projectType, smbRate, corporateRate, suggestedUse})
(:SegmentationCriterion {id, criterion, smbDescription, corporateDescription})
```

