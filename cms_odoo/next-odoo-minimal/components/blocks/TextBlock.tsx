import styles from './TextBlock.module.scss';

interface TextBlockProps {
  content: string;
}

export default function TextBlock({ content }: TextBlockProps) {
  return (
    <div className={styles.textBlock}>
      <p>{content}</p>
    </div>
  );
}
