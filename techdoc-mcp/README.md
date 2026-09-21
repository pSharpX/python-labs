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

## Check MCP Tools

### Using CURL

1. Get MCP-Session
```
curl -i \
  -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc":"2.0",
    "id":1,
    "method":"initialize",
    "params":{
      "protocolVersion":"2025-11-25",
      "capabilities":{},
      "clientInfo":{
        "name":"curl",
        "version":"1.0"
      }
    }
  }'
```


2. Get Tools List
```
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: ${mcp-session-id}" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```
