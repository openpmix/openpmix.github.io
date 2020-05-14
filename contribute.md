---
layout: page
title: Contribute
permalink: /contribute/
---

Would you like to contribute to PMIx?

We’d love it! One of the explicit goals of the PMIx community is to actively engage users, third party researchers, ISVs, hardware vendors… pretty much the entire HPC community. So if you’ve got some ideas, we’d love to hear them.

The PMIx community has three focus areas:

 - the PMIx Standard. Contributions to the Standard usually take the form of proposed modifications or requests for clarification of one or more portions of the published document. Equally welcome are proposals for new extensions to the Standard. The [PMIx Standard Governance Rules](/uploads/2020/04/pmix_governance-2020-04-15.pdf) describes rules for participation and making changes to the PMIx Standard. The governance document includes instructions for how to raise questions about the standard as well as how to propose changes to the standard.



 - the PMIx Reference Implementation Library (PRIL). When considering contributing to the library, it is important to remember that if you write new components (or modify existing components) for PRIL, they can be published independently of the main PRIL distribution. PRIL utilizes a dynamic plugin system that allows it to simply slurp up any binary plugin that is placed in the installed plugin directory. This means that you do not have to distribute all of the PRIL code — you can just publish your own plugins (proprietary or otherwise) on your web page, FTP site, etc. Users can download your plugins and add them to their existing PRIL installation.
Of course, we also welcome contributions to the open source PRIL repository! Naturally, we’re not giving out commit access to our repository to just anyone. We do need to maintain production-quality control on our code base. New contributors generally begin by posting pull requests or identifying issues while they gain some experience with our practices and become more familiar with the community.



 - the PMIx Reference RunTime Environment (PRRTE – pronounced “purtay”). Just like PRIL, PRRTE is built on a dynamic plugin system. Thus, all of the above description for PRIL applies equally here.

Probably the first thing you should do is join the conversation. The PMIx community has four methods of communication:

 - our [Slack channel](https://pmix-workspace.slack.com/) for developers. You’ll almost always find at least one community member there, and we regularly use the general channel for discussions on either of the libraries. You’ll also be able to track pull requests and commits to all three PMIx community areas on the feed channel.
 -issues posted on the [Standard](https://github.com/pmix/pmix-standard/issues), [PRIL](https://github.com/pmix/pmix/issues), or [PRRTE](https://github.com/pmix/prrte/issues) GitHub repository corresponding to the target of your question or comment.
 - community members meet every Thursday at noon US Pacific for a [telecon](https://recaptcha.open-mpi.org/pmix-recaptcha/) to discuss the Standard and the code libraries.
 - the [mailing list](https://groups.google.com/forum/#!forum/pmix). The list isn’t as heavily used as the other methods, but we do post announcements there and many of us monitor it for questions and comments

Next, you should look through the source code — get a Git clone of whichever area(s) interest you. PMIx is an active development effort — it is usually better to work with the most recent development version of the repository than the last stable release (especially for new projects). Contributions are submitted via pull requests against the target repository on Github. All commits must contain a “Signed-off-by” token in the commit message. This constitutes your agreement with the [PMIx Contributor’s Declaration](https://pmix.org/contributors-declaration/).

Here are several typical forms of contributions to PMIx:

 - Request clarification (e.g., open a new issue on the Standard repository) or suggest corrections to the Standard using either an issue or proposed new text in a pull request
 - Publish research results using your own modifications to the PRIL or PRRTE (e.g., performance enhancements, support for new environments, etc.). If possible, make the code available to others.
 - Write your own components for custom functionality (e.g., support a new network or back-end run-time environment).
 - Modify existing components for new functionality or performance enhancements
 - Suggest new functionality to the PMIx community.
 - Send complete bug reports and/or patches to the mailing lists. We always appreciate help in making PRIL and PRRTE better!
 - Submit code for new functionality to PRIL or PRRTE. We love code contributions! Keep in mind that code contributions must be robust enough to be suitable for widespread use.

Enough talk — we look forward to your participation!

