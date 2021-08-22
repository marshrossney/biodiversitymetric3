# The Biodiversity Metric: why academics, conservationists and ecologists are right to be worried

Natural England and collaborators recently released the third version of their '[Biodiversity Metric](http://publications.naturalengland.org.uk/publication/6049804846366720)' to a mixed reception.

The Biodiversity Metric specifies a procedure through which an existing or hypothetical area of land is assigned a numerical score that is supposed to represent its 'biodiversity value'.
The idea is that biodiversity losses due to housing developments are 'quantified' and can be offset by making comparable improvements elsewhere.
The upcoming [Environment Bill](https://www.gov.uk/government/publications/environment-bill-2020) will include a mandatory requirement for new proposals to demonstrate a post-development score that is 10% higher than the pre-development score, calculated using the Biodiversity Metric.

Unfortunately, the Biodiversity Metric is catastrophically flawed.
By adopting its principles and its terminology we put ourselves at risk of sleepwalking through decades of biodiversity loss before the fantasy evaporates.

These posts are an attempt to organise my criticisms and observations.
I hope that they might provide a useful reference, or at least an interesting read, for someone who is unsure as to the reliability of the Metric but who may find the numerical outputs somewhat opaque or even intimidating.
Even more, I hope that they contribute to an open and honest discussion of these issues, through which we might divise something better, or at least agree to stop fooling ourselves that we can have our cake and eat it.

**This is a work in progress. I expect to continue updating this page throughout autumn 2021.**
I should also be clear about the fact that I'm a physicist by training, not an ecologist.

## Contents

[Introduction and Motivation](introduction.md)

### The Mechanics of the Metric

I explain how the Metric works, why one should not consider Metric scores accurate indicators of biodiversity, and why the "percent Net Gain" outputs should never be used as evidence to support a development.


### Unintended Consequences and opportunity costs

I address the common defence that "the Biodiversity Metric cannot make things worse; it cannot be worse than nothing".


### Case study: Turnden Farmstead

I look at a particular example of the Biodiversity Metric being used (and very much abused) to support a major housing development on the site of a Medieval farmstead in a designated Area of Outstanding Natural Beauty. An appeal against this development is currently under way, fought by local residents, the AONB Unit and, ironically, Natural England themselves.


### Python code for testing the Metric

I have developed a simple Python package for performing these calculations, mainly because I wanted to play with the numbers and automate some tests which looked awkward to do with the Excel-based tool.

The code is available [here](https://github.com/marshrossney/biodiversitymetric3).
