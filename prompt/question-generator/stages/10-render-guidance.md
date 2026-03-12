Reads:
- full shared state
- selected output-mode module

Writes:
- no new analysis state
- renderer consumes the shared state as input

Possible outputs:
- research memo
- decision memo
- scenario tree
- monitoring dashboard
- investment worksheet
- deep-research prompt

Render rule:
- the render stage should not rethink the problem
- it should only format the accumulated state for the selected output mode
- it should use the shared state file as its sole analysis input
