# python-capsule-api
API bindings for capsule CRM

EXAMPLES
========

```python
capsule_api = CapsuleAPI(CAPSULE_NAME, CAPSULE_KEY)
opportunity = capsule_api.opportunity(12345)
print(opportunity.probability)
```
