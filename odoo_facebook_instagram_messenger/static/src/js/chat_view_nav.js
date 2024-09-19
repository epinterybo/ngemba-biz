/** @odoo-module **/

import {registerMessagingComponent} from "@mail/utils/messaging_component";
const {Component} = owl;

export class MessengerChatViewNav extends Component {
    setup() {
        super.setup();
    }
    mounted() {
        super.mounted();
        if (
            this.chatWindow &&
            this.chatWindow.thread &&
            this.chatWindow.thread.correspondent &&
            this.chatWindow.thread.correspondent.user
        ) {
            if(this.chatWindow.thread.isMessengerMsgs){
                this.onClickMessenger();
            }
            if (this.chatWindow.thread.isInstagramMsgs){
                this.onClickInstagram()
            }
        } else {
            this.onClickMessenger();
        }
    }
    render() {
        super.render();
        if (
            this.chatWindow &&
            this.chatWindow.thread &&
            this.chatWindow.thread.channel &&
            this.chatWindow.thread.channel.correspondent &&
            this.chatWindow.thread.channel.correspondent.persona.partner &&
            this.chatWindow.thread.channel.correspondent.persona.partner.user
        ) {
            if(this.chatWindow.thread.isWaMsgs){
                this.onClickMessenger();
            }
            if (this.chatWindow.thread.isInstagramMsgs){
                this.onClickInstagram()
            }
        } else {
            this.onClickMessenger();
        }
    }
    get chatWindow() {
        var chats = this.messaging.models["ChatWindow"]
            .all()
            .filter((chat) => chat.localId == this.props.chatWindowLocalId);
        return this.messaging && chats && chats[0];
    }
    //    onClickLive(){
    //        var message_div = false
    //        if(event){
    //            message_div = $(event.currentTarget)
    //        }
    //        if(this.chatWindow && this.chatWindow.thread){
    //            this.chatWindow.thread.update({isWaMsgs:false})
    //            //this.chatWindow.thread.refresh()
    //            if(message_div){
    //                setTimeout(function(){
    //                    if(message_div.closest('.o_ChatWindow').find('.o_ThreadView_messageList .o_MessageList_message') && message_div.closest('.o_ChatWindow').find('.o_ThreadView_messageList .o_MessageList_message')[message_div.closest('.o_ChatWindow').find('.o_ThreadView_messageList .o_MessageList_message').length - 1] && message_div.closest('.o_ChatWindow').find('.o_ThreadView_messageList .o_MessageList_message')[message_div.closest('.o_ChatWindow').find('.o_ThreadView_messageList .o_MessageList_message').length - 1].offsetTop){
    //                        message_div.closest('.o_ChatWindow').find('.o_ThreadView_messageList').animate({
    //                            scrollTop: message_div.closest('.o_ChatWindow').find('.o_ThreadView_messageList .o_MessageList_message')[message_div.closest('.o_ChatWindow').find('.o_ThreadView_messageList .o_MessageList_message').length - 1].offsetTop + 100,
    //                        }, 500);
    //                    }
    //                    setTimeout(function(){
    //                        if(message_div.closest('.o_ChatWindow').find('.o_ThreadView_messageList .o_MessageList_message') && message_div.closest('.o_ChatWindow').find('.o_ThreadView_messageList .o_MessageList_message')[message_div.closest('.o_ChatWindow').find('.o_ThreadView_messageList .o_MessageList_message').length - 1] && message_div.closest('.o_ChatWindow').find('.o_ThreadView_messageList .o_MessageList_message')[message_div.closest('.o_ChatWindow').find('.o_ThreadView_messageList .o_MessageList_message').length - 1].offsetTop){
    //                            message_div.closest('.o_ChatWindow').find('.o_ThreadView_messageList').animate({
    //                                scrollTop: message_div.closest('.o_ChatWindow').find('.o_ThreadView_messageList .o_MessageList_message')[message_div.closest('.o_ChatWindow').find('.o_ThreadView_messageList .o_MessageList_message').length - 1].offsetTop + 100,
    //                            }, 300);
    //                        }
    //                    }, 100);
    //                }, 400);
    //            }
    //        }
    //    }
    onClickMessenger() {
        var message_div = false;
        if (event) {
            message_div = $(event.currentTarget);
        }
        if (this.chatWindow && this.chatWindow.thread) {
            this.chatWindow.thread.update({isMessengerMsgs:true})
//            this.chatWindow.thread.refresh()
            if (message_div) {
                setTimeout(function () {
                    if (
                        message_div
                            .closest(".o_ChatWindow")
                            .find(".o_ThreadView_messageList .o_MessageList_message") &&
                        message_div
                            .closest(".o_ChatWindow")
                            .find(".o_ThreadView_messageList .o_MessageList_message")[
                            message_div
                                .closest(".o_ChatWindow")
                                .find(
                                    ".o_ThreadView_messageList .o_MessageList_message"
                                ).length - 1
                        ] &&
                        message_div
                            .closest(".o_ChatWindow")
                            .find(".o_ThreadView_messageList .o_MessageList_message")[
                            message_div
                                .closest(".o_ChatWindow")
                                .find(
                                    ".o_ThreadView_messageList .o_MessageList_message"
                                ).length - 1
                        ].offsetTop
                    ) {
                        message_div
                            .closest(".o_ChatWindow")
                            .find(".o_ThreadView_messageList")
                            .animate(
                                {
                                    scrollTop:
                                        message_div
                                            .closest(".o_ChatWindow")
                                            .find(
                                                ".o_ThreadView_messageList .o_MessageList_message"
                                            )[
                                            message_div
                                                .closest(".o_ChatWindow")
                                                .find(
                                                    ".o_ThreadView_messageList .o_MessageList_message"
                                                ).length - 1
                                        ].offsetTop + 100,
                                },
                                500
                            );
                    }
                    setTimeout(function () {
                        if (
                            message_div
                                .closest(".o_ChatWindow")
                                .find(
                                    ".o_ThreadView_messageList .o_MessageList_message"
                                ) &&
                            message_div
                                .closest(".o_ChatWindow")
                                .find(
                                    ".o_ThreadView_messageList .o_MessageList_message"
                                )[
                                message_div
                                    .closest(".o_ChatWindow")
                                    .find(
                                        ".o_ThreadView_messageList .o_MessageList_message"
                                    ).length - 1
                            ] &&
                            message_div
                                .closest(".o_ChatWindow")
                                .find(
                                    ".o_ThreadView_messageList .o_MessageList_message"
                                )[
                                message_div
                                    .closest(".o_ChatWindow")
                                    .find(
                                        ".o_ThreadView_messageList .o_MessageList_message"
                                    ).length - 1
                            ].offsetTop
                        ) {
                            message_div
                                .closest(".o_ChatWindow")
                                .find(".o_ThreadView_messageList")
                                .animate(
                                    {
                                        scrollTop:
                                            message_div
                                                .closest(".o_ChatWindow")
                                                .find(
                                                    ".o_ThreadView_messageList .o_MessageList_message"
                                                )[
                                                message_div
                                                    .closest(".o_ChatWindow")
                                                    .find(
                                                        ".o_ThreadView_messageList .o_MessageList_message"
                                                    ).length - 1
                                            ].offsetTop + 100,
                                    },
                                    300
                                );
                        }
                    }, 100);
                }, 400);
            }
        }
    }

    onClickInstagram() {
        var message_div = false;
        if (event) {
            message_div = $(event.currentTarget);
        }
        if (this.chatWindow && this.chatWindow.thread) {
            this.chatWindow.thread.update({isInstagramMsgs:true})
//            this.chatWindow.thread.refresh()
            if (message_div) {
                setTimeout(function () {
                    if (
                        message_div
                            .closest(".o_ChatWindow")
                            .find(".o_ThreadView_messageList .o_MessageList_message") &&
                        message_div
                            .closest(".o_ChatWindow")
                            .find(".o_ThreadView_messageList .o_MessageList_message")[
                            message_div
                                .closest(".o_ChatWindow")
                                .find(
                                    ".o_ThreadView_messageList .o_MessageList_message"
                                ).length - 1
                        ] &&
                        message_div
                            .closest(".o_ChatWindow")
                            .find(".o_ThreadView_messageList .o_MessageList_message")[
                            message_div
                                .closest(".o_ChatWindow")
                                .find(
                                    ".o_ThreadView_messageList .o_MessageList_message"
                                ).length - 1
                        ].offsetTop
                    ) {
                        message_div
                            .closest(".o_ChatWindow")
                            .find(".o_ThreadView_messageList")
                            .animate(
                                {
                                    scrollTop:
                                        message_div
                                            .closest(".o_ChatWindow")
                                            .find(
                                                ".o_ThreadView_messageList .o_MessageList_message"
                                            )[
                                            message_div
                                                .closest(".o_ChatWindow")
                                                .find(
                                                    ".o_ThreadView_messageList .o_MessageList_message"
                                                ).length - 1
                                        ].offsetTop + 100,
                                },
                                500
                            );
                    }
                    setTimeout(function () {
                        if (
                            message_div
                                .closest(".o_ChatWindow")
                                .find(
                                    ".o_ThreadView_messageList .o_MessageList_message"
                                ) &&
                            message_div
                                .closest(".o_ChatWindow")
                                .find(
                                    ".o_ThreadView_messageList .o_MessageList_message"
                                )[
                                message_div
                                    .closest(".o_ChatWindow")
                                    .find(
                                        ".o_ThreadView_messageList .o_MessageList_message"
                                    ).length - 1
                            ] &&
                            message_div
                                .closest(".o_ChatWindow")
                                .find(
                                    ".o_ThreadView_messageList .o_MessageList_message"
                                )[
                                message_div
                                    .closest(".o_ChatWindow")
                                    .find(
                                        ".o_ThreadView_messageList .o_MessageList_message"
                                    ).length - 1
                            ].offsetTop
                        ) {
                            message_div
                                .closest(".o_ChatWindow")
                                .find(".o_ThreadView_messageList")
                                .animate(
                                    {
                                        scrollTop:
                                            message_div
                                                .closest(".o_ChatWindow")
                                                .find(
                                                    ".o_ThreadView_messageList .o_MessageList_message"
                                                )[
                                                message_div
                                                    .closest(".o_ChatWindow")
                                                    .find(
                                                        ".o_ThreadView_messageList .o_MessageList_message"
                                                    ).length - 1
                                            ].offsetTop + 100,
                                    },
                                    300
                                );
                        }
                    }, 100);
                }, 400);
            }
        }
    }
}

Object.assign(MessengerChatViewNav, {
    props: {
        chatWindowLocalId: String,
    },
    template: "odoo_facebook_instagram_messenger.MessengerChatViewNav",
});

registerMessagingComponent(MessengerChatViewNav);
