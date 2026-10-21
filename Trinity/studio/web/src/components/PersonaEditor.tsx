import {
  BlockTypeSelect,
  BoldItalicUnderlineToggles,
  CreateLink,
  DiffSourceToggleWrapper,
  InsertCodeBlock,
  InsertTable,
  ListsToggle,
  MDXEditor,
  UndoRedo,
  codeBlockPlugin,
  codeMirrorPlugin,
  diffSourcePlugin,
  headingsPlugin,
  linkDialogPlugin,
  linkPlugin,
  listsPlugin,
  markdownShortcutPlugin,
  quotePlugin,
  tablePlugin,
  thematicBreakPlugin,
  toolbarPlugin,
} from "@mdxeditor/editor";
import "@mdxeditor/editor/style.css";

type Props = {
  editorKey: string;
  markdown: string;
  onChange: (markdown: string) => void;
};

const plugins = [
  headingsPlugin(),
  listsPlugin(),
  quotePlugin(),
  thematicBreakPlugin(),
  linkPlugin(),
  linkDialogPlugin(),
  tablePlugin(),
  codeBlockPlugin({ defaultCodeBlockLanguage: "txt" }),
  codeMirrorPlugin({ codeBlockLanguages: { python: "Python", txt: "Text", "": "Text" } }),
  markdownShortcutPlugin(),
  diffSourcePlugin({ viewMode: "rich-text" }),
  toolbarPlugin({
    toolbarContents: () => (
      <DiffSourceToggleWrapper>
        <UndoRedo />
        <BlockTypeSelect />
        <BoldItalicUnderlineToggles options={["Bold", "Italic"]} />
        <ListsToggle />
        <CreateLink />
        <InsertTable />
        <InsertCodeBlock />
      </DiffSourceToggleWrapper>
    ),
  }),
];

export default function PersonaEditor({ editorKey, markdown, onChange }: Props) {
  return (
    <div className="persona-mdx-wrap">
      <MDXEditor
        key={editorKey}
        markdown={markdown}
        plugins={plugins}
        onChange={onChange}
        contentEditableClassName="persona-mdx-content"
      />
    </div>
  );
}
