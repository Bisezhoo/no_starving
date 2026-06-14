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

  it("submits on Enter key", async () => {
    const wrapper = mount(MessageComposer, { props: { disabled: false } });

    await wrapper.find("textarea").setValue("红烧肉怎么做");
    await wrapper.find("textarea").trigger("keydown", { key: "Enter" });

    expect(wrapper.emitted("send")).toHaveLength(1);
    expect(wrapper.emitted("send")![0]).toEqual(["红烧肉怎么做"]);
    // draft should be cleared
    expect((wrapper.find("textarea").element as HTMLTextAreaElement).value).toBe("");
  });

  it("does not submit on Ctrl+Enter", async () => {
    const wrapper = mount(MessageComposer, { props: { disabled: false } });

    await wrapper.find("textarea").setValue("红烧肉怎么做");
    await wrapper.find("textarea").trigger("keydown", {
      key: "Enter",
      ctrlKey: true,
    });

    expect(wrapper.emitted("send")).toBeUndefined();
  });

  it("does not submit on Meta+Enter", async () => {
    const wrapper = mount(MessageComposer, { props: { disabled: false } });

    await wrapper.find("textarea").setValue("红烧肉怎么做");
    await wrapper.find("textarea").trigger("keydown", {
      key: "Enter",
      metaKey: true,
    });

    expect(wrapper.emitted("send")).toBeUndefined();
  });
});
