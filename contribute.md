---
layout: page
title: Contribute
permalink: /contribute/
---

PMIx Reference Implementation Library (PRIL)
--------------------------------------------

When considering contributing to the
[library](https://github.com/openpmix/openpmix), it is important to remember
that if you write new components (or modify existing components) for PRIL,
they can be published independently of the main PRIL distribution. PRIL
utilizes a dynamic plugin system that allows it to simply slurp up any
binary plugin that is placed in the installed plugin directory. This means
that you do not have to distribute all of the PRIL code — you can just
publish your own plugins (proprietary or otherwise) on your web page, FTP
site, etc. Users can download your plugins and add them to their existing
PRIL installation.  Of course, we also welcome contributions to the open
source PRIL repository! Naturally, we’re not giving out commit access to our
repository to just anyone. We do need to maintain production-quality control
on our code base. New contributors generally begin by posting pull requests
or identifying issues while they gain some experience with our practices and
become more familiar with the community.

PMIx Reference RunTime Environment (PRRTE)
------------------------------------------

Just like PRIL, [PRRTE](https://github.com/openpmix/prrte) (pronounced
"purtay") is built on a dynamic plugin system. Thus, all of the above
description for PRIL applies equally here.

PMIx Standard
-------------
 - The [PMIx Standard](https://pmix.github.io) itself.


Communication Channels
----------------------

Probably the first thing you should do is join the conversation.

 - [Slack channel](https://pmix-workspace.slack.com/) for developers. You’ll
   almost always find at least one community member there, and we regularly
   use the general channel for discussions on either of the libraries.
   You’ll also be able to track pull requests and commits to all three PMIx
   community areas on the feed channel.

 - Issues posted on the [PRIL](https://github.com/pmix/pmix/issues), or
   [PRRTE](https://github.com/pmix/prrte/issues)
   GitHub repository corresponding to the target of your question or comment.

 - Community members meet every Thursday at noon US Pacific for a
   [telecon](https://recaptcha.open-mpi.org/pmix-recaptcha/) to discuss the
   the implementation aspects of the PMIx Standard.

 - [Mailing list](https://groups.google.com/forum/#!forum/pmix). The list
   is not as heavily used as the other methods, but we do post announcements
   there and many of us monitor it for questions and comments

Contributions to Code
---------------------

Next, you should look through the source code — get a Git clone of whichever
area(s) interest you. PMIx is an active development effort — it is usually
better to work with the most recent development version of the repository
than the last stable release (especially for new projects). Contributions
are submitted via pull requests against the target repository on Github. All
commits must contain a "Signed-off-by" token in the commit message. This
constitutes your agreement with the [OpenPMIx Contributor’s
Declaration](/contributors-declaration/).

Here are several typical forms of contributions to OpenPMIx:

 - Publish research results using your own modifications to the PRIL or
   PRRTE (e.g., performance enhancements, support for new environments,
   etc.). If possible, make the code available to others.
 - Write your own components for custom functionality (e.g., support a new
   network or back-end run-time environment).
 - Modify existing components for new functionality or performance enhancements
 - Suggest new functionality to the PMIx community.
 - Send complete bug reports and/or patches to the mailing lists. We always
   appreciate help in making PRIL and PRRTE better!
 - Submit code for new functionality to PRIL or PRRTE. We love code
   contributions! Keep in mind that code contributions must be robust enough
   to be suitable for widespread use.

Enough talk — we look forward to your participation!

