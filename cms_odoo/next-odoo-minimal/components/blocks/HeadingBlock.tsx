import styles from './HeadingBlock.module.scss';

interface HeadingBlockProps {
  text: string;
  level: 'h1' | 'h2' | 'h3' | 'h4';
}

export default function HeadingBlock({ text, level }: HeadingBlockProps) {
  const Tag = level;

  return <Tag className={styles[level]}>{text}</Tag>;
}
