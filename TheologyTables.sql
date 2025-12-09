-- ==========================================
-- Upgrade Script for theology_verses
-- ==========================================

-- 1. Set role, database, and schema
USE ROLE ACCOUNTADMIN;
USE DATABASE SNOWFLAKE_LEARNING_DB;
USE SCHEMA PUBLIC;

-- 2. Create table if it doesn't exist (with your sample verses)
CREATE TABLE IF NOT EXISTS theology_verses (
    keyword STRING,
    verse STRING
);

-- 3. Insert sample verses (your full dataset can be added)
INSERT INTO theology_verses (keyword, verse) VALUES
('meaning_of_life', 'Dhammapada 277 — All things arise and pass away. When one truly sees this truth, suffering ends and wisdom begins.'),
('why_are_we_here', 'Dhammapada 276 — The Buddha shows the path; each person must walk it with effort, awareness, and understanding.'),
('suffering', 'Dhammapada 216 — Craving gives rise to sorrow and fear; when craving fades, so too do sorrow and fear.'),
('anger', 'Dhammapada 223 — Conquer anger with love, evil with goodness, greed with generosity, and lies with truth.'),
('attachment', 'Dhammapada 211 — From attachment comes sorrow; free from attachment, the heart rests in lasting peace.'),
('death', 'Dhammapada 128 — Not even the swiftest can escape death; it comes to all, wise and foolish alike.'),
('desire', 'Dhammapada 216 — Desire gives birth to grief and fear; one who is free from desire knows neither grief nor fear.'),
('mind', 'Dhammapada 33 — The mind is restless and hard to control; like a skilled fletcher, the wise straighten it.'),
('peace', 'Dhammapada 201 — Victory breeds hatred; the peaceful live with ease, renouncing both victory and defeat.'),
('life', 'Dhammapada 85 — Few reach the far shore of liberation; most remain wandering along the banks of illusion.'),
('speech', 'Dhammapada 231 — Guard your words carefully; speak only that which brings peace and harmony.'),
('truth', 'Dhammapada 224 — Speak truth, live without anger, and give freely; this is the path of the virtuous.'),
('patience', 'Dhammapada 184 — Patience and forgiveness are the highest practices; the wise are gentle and disciplined.'),
('effort', 'Dhammapada 276 — Strive earnestly; the Buddhas only show the way — you must walk it yourself.'),
('wisdom', 'Dhammapada 256 — The wise do not judge by appearances; they discern truth beyond bias and desire.'),
('compassion', 'Dhammapada 270 — A noble heart harms no living being and brings compassion to all creatures.'),
('generosity', 'Dhammapada 224 — Give freely without expecting reward; generosity purifies the heart and mind.'),
('hatred', 'Dhammapada 5 — Hatred never ends through hatred, but only through love; this is the eternal law.'),
('greed', 'Dhammapada 355 — Wealth destroys the foolish who crave it, like a flood sweeping away a sleeping village.'),
('envy', 'Dhammapada 365 — Conquer envy with contentment and rejoice in the happiness of others.'),
('mindfulness', 'Dhammapada 35 — The disciplined mind brings happiness; a wandering mind brings sorrow and confusion.'),
('meditation', 'Dhammapada 282 — Through meditation and wisdom, one purifies oneself and finds lasting peace.'),
('self_control', 'Dhammapada 103 — Greater than conquering a thousand men is conquering one’s own mind.'),
('focus', 'Dhammapada 25 — The wise, focused and resolute, climb the mountain of wisdom and find freedom.'),
('ignorance', 'Dhammapada 13 — The fool lives in darkness, counting others’ wealth while ignoring his own path.'),
('awakening', 'Dhammapada 21 — The mindful never die; awareness is the path to the deathless state.'),
('awareness', 'Dhammapada 23 — The alert and mindful advance like swift horses, leaving the careless far behind.'),
('discipline', 'Dhammapada 157 — Discipline purifies the heart; no one can cleanse another’s mind for them.'),
('temptation', 'Dhammapada 347 — The craving mind spins its own web, trapping itself until wisdom cuts it free.'),
('ego', 'Dhammapada 94 — The awakened one is free from pride and attachment; calm as a still lake.'),
('friendship', 'Dhammapada 61 — Better a solitary life than company with the foolish, who lead one astray.'),
('evil', 'Dhammapada 117 — Avoid evil, cultivate good, and purify the mind to follow the path of the wise.'),
('good_deeds', 'Dhammapada 122 — Do not overlook small good deeds; they accumulate like drops filling a jar.'),
('forgiveness', 'Dhammapada 223 — Conquer anger with love and forgiveness; this is the mark of a noble heart.'),
('path', 'Dhammapada 183 — Avoid evil, do good, and purify the mind; this is the teaching of all Buddhas.'),
('truth_seeking', 'Dhammapada 354 — The gift of truth surpasses all other gifts; cherish it above wealth.'),
('freedom', 'Dhammapada 348 — Having abandoned craving and attachment, one is truly free and serene.'),
('contentment', 'Dhammapada 204 — Health, contentment, and trust are the greatest treasures one can possess.'),
('discipleship', 'Dhammapada 276 — The teacher shows the way; the disciple must walk it diligently and wisely.'),
('purity', 'Dhammapada 183 — Purity of thought, word, and deed is the essence of the enlightened path.'),
('happy', 'Dhammapada 204 — Joy arises from contentment and mindfulness; those who cling to desire know little joy.'),
('kindness', 'Dhammapada 223 — Kindness to all beings, even enemies, purifies the mind and softens the heart.'),
('humility', 'Dhammapada 89 — The humble avoid arrogance; like a tree bending in wind, they endure and flourish.'),
('gratitude', 'Dhammapada 212 — Appreciating the blessings of life, no matter how small, leads to lasting peace.'),
('resilience', 'Dhammapada 80 — The steadfast endure hardship without complaint, like mountains standing through storms.'),
('clarity', 'Dhammapada 33 — A clear mind sees the true nature of all things and avoids illusion.'),
('forbearance', 'Dhammapada 184 — Bearing insult and harm without anger is the hallmark of the wise.'),
('sincerity', 'Dhammapada 224 — Actions in line with sincere intention bring harmony and inner peace.'),
('moderation', 'Dhammapada 372 — Excess and indulgence lead to suffering; moderation brings freedom.'),
('die', 'Dhammapada 128 — Mindful of death, one lives fully, aware of the fleeting nature of all things.'),
('selflessness', 'Dhammapada 94 — Letting go of ego and selfishness allows the heart to be free and compassionate.'),
('patience_in_practice', 'Dhammapada 184 — True practice requires patience; sudden haste leads to stumbling.'),
('equanimity', 'Dhammapada 201 — Even in success or failure, the mind remains balanced, steady, and calm.'),
('reflection', 'Dhammapada 277 — Reflecting on impermanence deepens understanding and lessens attachment.'),
('fuck', 'Dhammapada 231 — Thoughtful and disciplined speech brings peace to oneself and others. Mind your words; harsh speech harms both speaker and listener.'),
('shit', 'Dhammapada 231 — Words can wound; choose carefully. Reflect before speaking, and cultivate restraint in all speech.'),
('bitch', 'Dhammapada 223 — Conquer anger with love and patience. Insulting words only feed suffering; speak with compassion instead.'),
('damn', 'Dhammapada 5 — Hatred never ends through anger or cursing; only calm, kind speech brings peace.'),
('asshole', 'Dhammapada 270 — A noble heart harms no being; consider your words and the impact they have on others.'),
('learning', 'Dhammapada 276 — Learning and applying wisdom steadily leads one along the path to liberation.'),
('preparation', 'Dhammapada 103 — Cultivate the mind daily; preparation prevents the pitfalls of desire and distraction.'),
('serenity', 'Dhammapada 201 — Serenity arises when the mind is free from craving and rests in the present moment.'),
('understanding', 'Dhammapada 256 — Understanding the nature of mind and world is the root of wisdom and compassion.');


-- 6. Add tag column
ALTER TABLE theology_verses
ADD COLUMN IF NOT EXISTS tag STRING;

-- 7. Add keywords column (AI-generated)
ALTER TABLE theology_verses
ADD COLUMN IF NOT EXISTS keywords STRING;  -- Snowflake AI returns string

-- 8. Add theme column (AI-classified)
ALTER TABLE theology_verses
ADD COLUMN IF NOT EXISTS theme STRING;
