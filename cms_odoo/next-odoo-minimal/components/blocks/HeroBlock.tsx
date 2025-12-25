import styles from './HeroBlock.module.scss';

interface HeroBlockProps {
  title: string;
  subtitle: string;
  buttonText?: string;
  buttonUrl?: string;
  backgroundImage?: string;
}

export default function HeroBlock({
  title,
  subtitle,
  buttonText,
  buttonUrl,
  backgroundImage
}: HeroBlockProps) {
  const bgStyle = backgroundImage
    ? `linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url(${backgroundImage})`
    : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';

  return (
    <div className={styles.heroBlock} style={{ background: bgStyle }}>
      <h1>{title}</h1>
      <p className={styles.subtitle}>{subtitle}</p>
      {buttonText && buttonUrl && (
        <a href={buttonUrl} className={styles.heroButton}>
          {buttonText}
        </a>
      )}
    </div>
  );
}
