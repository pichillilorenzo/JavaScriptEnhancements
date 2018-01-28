# Contribute

## Introduction

First, thank you for considering contributing to JavaScript Enhancements! It's people like you that make the open source community such a great community! 😊

We welcome any type of contribution, not only code. You can help with 
- **QA**: file bug reports, the more details you can give the better (e.g. screenshots with the console open)
- **Marketing**: writing blog posts, howto's, videos, ...
- **Code**: take a look at the [open issues](issues). Even if you can't write code, commenting on them, showing that you care about a given issue matters. It helps us triage them.
- **Money**: we welcome financial contributions in full transparency on [Open Collective](https://opencollective.com/javascriptenhancements) or using [PayPal](https://www.paypal.me/LorenzoPichilli).

## Your First Contribution

Working on your first Pull Request? You can learn how from this *free* series, [How to Contribute to an Open Source Project on GitHub](https://egghead.io/series/how-to-contribute-to-an-open-source-project-on-github).

## Submitting code

Any code change should be submitted as a pull request. The description should explain what the code does and give steps to execute it. If necessary, the description should also contain screenshots showing up the new behaviour.

You can notice that in the main folder of the plugin there is a file named something like `_generated_2018_01_28_at_03_01_29.py`. This file is compiled executing `python3 make/setup.py` and it contains the whole plugin code. So, if you want to make changes/updates to this plugin, don't change this file. Instead change the other files that you can find in the `helper`, `project` and `flow` folders. The `make/_init.py` file contains the main code to boot up the plugin, with various constants.

Syntax accepted by `make/setup.py`:
* `${include ./helper/Hook.py}`: with `./` at the beginning of the path, you are pointing to the root path of the plugin folder, like an "absolute path" 
* `${include javascript_completions/main.py}`: in this case this is a relative path to the current folder

With this, you can separate your code in different files that will be added to the final compiled code.

To test the plugin changes/updates quickly, you can execute `python3 make/watch.py`. So, for every changes that you make in the code, it will call automatically `make/setup.py`. If you add new files while you are using `python3 make/watch.py`, it may require restart the command in order to allow the change/update recognition of these new files.

## Code review process

The bigger the pull request, the longer it will take to review and merge. Try to break down large pull requests in smaller chunks that are easier to review and merge.
It is also always helpful to have some context for your pull request. What was the purpose? Why does it matter to you?

## Issues/Questions

If you have any problems, create an [issue](issue) (protip: do a quick search first to see if someone else didn't ask the same question before!). For small questions, you can use [![Gitter](https://img.shields.io/gitter/room/nwjs/nw.js.svg)](https://gitter.im/JavaScriptEnhancements/Lobby).

Email me for any questions or doubts about this project on: [pichillilorenzo@gmail.com](mailto:pichillilorenzo@gmail.com)

## Feature request/enhancement

For feature requests/enhancement, create an issue or use [![Gitter](https://img.shields.io/gitter/room/nwjs/nw.js.svg)](https://gitter.im/JavaScriptEnhancements/Features).

## Financial contributions

If this project help you reduce time to develop and also you like it, please support it with a donation on [Open Collective](https://opencollective.com/javascriptenhancements) or using [PayPal](https://www.paypal.me/LorenzoPichilli) 😄👍. Thanks!

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.me/LorenzoPichilli)
<a href="https://opencollective.com/javascriptenhancements/donate" target="_blank">
  <img alt="opencollective" src="https://opencollective.com/javascriptenhancements/donate/button@2x.png?color=blue" width=300 />
</a>

## Credits

### Contributors

Thank you to all the people who have already contributed to JavaScript Enhancements!
<a href="graphs/contributors"><img src="https://opencollective.com/javascriptenhancements/contributors.svg?width=890" /></a>


### Backers

Thank you to all our backers! [[Become a backer](https://opencollective.com/javascriptenhancements#backer)]

<a href="https://opencollective.com/javascriptenhancements#backers" target="_blank"><img src="https://opencollective.com/javascriptenhancements/backers.svg?width=890"></a>


### Sponsors

Thank you to all our sponsors! (please ask your company to also support this open source project by [becoming a sponsor](https://opencollective.com/javascriptenhancements#sponsor))

<a href="https://opencollective.com/javascriptenhancements/sponsor/0/website" target="_blank"><img src="https://opencollective.com/javascriptenhancements/sponsor/0/avatar.svg"></a>
<a href="https://opencollective.com/javascriptenhancements/sponsor/1/website" target="_blank"><img src="https://opencollective.com/javascriptenhancements/sponsor/1/avatar.svg"></a>
<a href="https://opencollective.com/javascriptenhancements/sponsor/2/website" target="_blank"><img src="https://opencollective.com/javascriptenhancements/sponsor/2/avatar.svg"></a>
<a href="https://opencollective.com/javascriptenhancements/sponsor/3/website" target="_blank"><img src="https://opencollective.com/javascriptenhancements/sponsor/3/avatar.svg"></a>
<a href="https://opencollective.com/javascriptenhancements/sponsor/4/website" target="_blank"><img src="https://opencollective.com/javascriptenhancements/sponsor/4/avatar.svg"></a>
<a href="https://opencollective.com/javascriptenhancements/sponsor/5/website" target="_blank"><img src="https://opencollective.com/javascriptenhancements/sponsor/5/avatar.svg"></a>
<a href="https://opencollective.com/javascriptenhancements/sponsor/6/website" target="_blank"><img src="https://opencollective.com/javascriptenhancements/sponsor/6/avatar.svg"></a>
<a href="https://opencollective.com/javascriptenhancements/sponsor/7/website" target="_blank"><img src="https://opencollective.com/javascriptenhancements/sponsor/7/avatar.svg"></a>
<a href="https://opencollective.com/javascriptenhancements/sponsor/8/website" target="_blank"><img src="https://opencollective.com/javascriptenhancements/sponsor/8/avatar.svg"></a>
<a href="https://opencollective.com/javascriptenhancements/sponsor/9/website" target="_blank"><img src="https://opencollective.com/javascriptenhancements/sponsor/9/avatar.svg"></a>

<!-- This `CONTRIBUTING.md` is based on @nayafia's template https://github.com/nayafia/contributing-template -->
