import styles from './HtmlBlock.module.scss';

interface HtmlBlockProps {
  content: string;
}

export default function HtmlBlock({ content }: HtmlBlockProps) {
  return (
    <div
      className={styles.htmlBlock}
      dangerouslySetInnerHTML={{ __html: content }}
    />
  );
}
