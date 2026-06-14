import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import MessageComposer from "../src/components/MessageComposer.vue";

describe("MessageComposer", () => {
  it("does not submit blank messages", async () => {
    const wrapper = mount(MessageComposer, { props: { disabled: false } });

    await wrapper.find("textarea").setValue("   ");
    await wrapper.find("form").trigger("submit.prevent");

    expect(wrapper.emitted("send")).toBeUndefined();
  });
});
