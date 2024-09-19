/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { attr, one } from '@mail/model/model_field';
import { clear, FieldCommand, link, unlink, unlinkAll } from '@mail/model/model_field_command';

registerPatch({
    name: 'Thread',
        fields: {
            isMessengerMsgs: attr({
                default: false,
            }),
            isInstagramMsgs: attr({
                default: false,
            }),
        }
});

registerPatch({
    name: 'Channel',
        fields: {
            isMessengerMsgs: attr({
                default: false,
            }),
            isInstagramMsgs: attr({
                default: false,
            }),

            correspondent: {
                compute() {
                    if (this.channel_type === 'channel') {
                        return clear();
                    }
                    const correspondents1 = this.channelMembers
                        .filter(member => member.persona && member.persona.partner && !member.isMemberOfCurrentUser)
                        .map(member => member.persona.partner);
                    const correspondents = this.channelMembers.filter(partner =>
                        partner !== this.messaging.currentPartner
                    );
                    var partner = correspondents.filter(r => typeof(r.user) == "undefined")
                    if (correspondents.length > 0) {
                        // 2 members chat
                        if(partner.length > 0){
                            return link(partner[0]);
                        }
                        return link(correspondents[0]);
                    }
                    if (this.members.length === 1) {
                        // chat with oneself
                        return link(this.members[0]);
                    }
                    return unlink();
                }

            },

        /**
         * When we refresh the page, Read Messages Showing Unread on DiscussSidebarCategoryItem OR Channel OR Thread
         * this.serverMessageUnreadCounter commented line on Discuss Screen.
         */
        localMessageUnreadCounter: {
            compute() {
                if (!this.thread) {
                    return clear();
                }
                // By default trust the server up to the last message it used
                // because it's not possible to do better.
                // this.serverMessageUnreadCounter commented line here.
//                let baseCounter = this.serverMessageUnreadCounter;
                let baseCounter;
                let countFromId = this.thread.serverLastMessage ? this.thread.serverLastMessage.id : 0;
                // But if the client knows the last seen message that the server
                // returned (and by assumption all the messages that come after),
                // the counter can be computed fully locally, ignoring potentially
                // obsolete values from the server.
                const firstMessage = this.thread.orderedMessages[0];
                if (
                    firstMessage &&
                    this.thread.lastSeenByCurrentPartnerMessageId &&
                    this.thread.lastSeenByCurrentPartnerMessageId >= firstMessage.id
                ) {
                    baseCounter = 0;
                    countFromId = this.thread.lastSeenByCurrentPartnerMessageId;
                }
                // Include all the messages that are known locally but the server
                // didn't take into account.
                return this.thread.orderedMessages.reduce((total, message) => {
                    if (message.id <= countFromId) {
                        return total;
                    }
                    return total + 1;
                }, baseCounter);
            },
        },

        }
});
//
///**
// * When click on DiscussSidebarCategoryItem OR channel_type = chat
// * By Default, We have Selected WhatsApp Chat Tab Active on Discuss Screen.
// */
registerPatch({
    name: 'DiscussSidebarCategoryItem',
        recordMethods: {
            onClick(ev) {
                if (this.thread.channel.channel_type == 'chat') {
                    this.thread.open();
                    this.thread.update({isMessengerMsgs:true}); // WhatsApp Tab will Open By Default when we click on DiscussSidebarCategoryItem
                    if(this.thread.messaging && this.thread.messaging.wa_thread_view){ // && this.thread.messaging.wa_thread_view.state.nav_active == 'partner'
                        this.thread.messaging.wa_thread_view.tabPartner(); // TabPartner will open when we click on DiscussSidebarCategoryItem
                    }
                }
                else {
                    this.thread.open();
                }
            },
        },
});
//
//
///**
// * Left/Right Chat isInChatWindow and isInDiscuss
// */
registerPatch({
    name: 'MessageView',
    fields: {
        isInChatWindowAndIsAlignedRight: {
            compute() {
                if (this.message && (this.isInChatWindow || this.isInDiscuss)) {
                    var isInternalUser = false
                    if (this.message && this.message.author && this.message.author.user && this.message.author.user.isInternalUser){
                        isInternalUser = true
                    }
                    return Boolean(
                        (this.isInChatWindow || this.isInDiscuss) &&
                        this.message &&
                        this.message.isCurrentUserOrGuestAuthor || isInternalUser
                    );
                } else { return false; }
            },
        },
        isInChatWindowAndIsAlignedLeft: {
            compute() {
                return Boolean(
                    (this.isInChatWindow || this.isInDiscuss) &&
                    this.message &&
                    this.message.isCurrentUserOrGuestAuthor
                );
            },
        },
    },
});
//
///**
// * Left/Right attachmentList isInChatWindow and isInDiscuss
// */
registerPatch({
    name: 'AttachmentList',
    fields: {
        isInChatWindowAndIsAlignedRight: {
            compute() {
                if (this.message && (this.isInChatWindow || this.isInDiscuss)) {
                    var isInternalUser = false
                    if (this.message && this.message.author && this.message.author.user && this.message.author.user.isInternalUser){
                    isInternalUser = true
                    }
                    return Boolean(
                        (this.isInChatWindow || this.isInDiscuss) &&
                        this.isCurrentUserOrGuestAuthor || isInternalUser
                    );
                } else { return false;}
            },
        },
        isInChatWindowAndIsAlignedLeft: {
            compute() {
                return Boolean(
                    (this.isInChatWindow || this.isInDiscuss) &&
                    this.isCurrentUserOrGuestAuthor
                );
            },
        },
    },
});
///**
// * Error Message showing in Chat isInChatWindow and isInDiscuss
// */
//registerPatch({
//    name: 'Message',
//    modelMethods: {
//        /**
//         * @override
//         */
//        convertData(data) {
//            const res = this._super(data);
//
//            if ('wa_delivery_status' in data) {
//                res.im_delivery_status = data.im_delivery_status;
//            }
//            if ('wa_error_message' in data) {
//                res.wa_error_message = data.wa_error_message;
//            }
//            if ('wp_status' in data) {
//                res.wp_status = data.wp_status;
//            }
//            return res;
//        },
//    },
//    fields: {
//        im_delivery_status: attr({
//            default: false,
//        }),
//        im_error_message: attr({
//            default: false,
//        }),
//        im_status: attr({
//            default: false,
//        }),
//    },
//});
