import {
    createStyles,
    Container,
    Title,
    Text,
    List,
    ThemeIcon,
    rem,
    Paper,
  } from '@mantine/core';
  import { IconCheck } from '@tabler/icons-react';
//   import image from './image.svg';
  
  const useStyles = createStyles((theme) => ({
    inner: {
      display: 'flex',
      justifyContent: 'space-between',
      paddingTop: `calc(${theme.spacing.xl} * 4)`,
      paddingBottom: `calc(${theme.spacing.xs} * 4)`,
    },
  
    content: {
      marginRight: `calc(${theme.spacing.xl} * 3)`,
  
      [theme.fn.smallerThan('md')]: {
        maxWidth: '100%',
        marginRight: 0,
      },
    },
  
    title: {
      color: theme.colorScheme === 'dark' ? theme.white : theme.black,
      fontFamily: `Greycliff CF, ${theme.fontFamily}`,
      fontSize: rem(44),
      lineHeight: 1.2,
      fontWeight: 900,
  
      [theme.fn.smallerThan('xs')]: {
        fontSize: rem(28),
      },
    },
  
    control: {
      [theme.fn.smallerThan('xs')]: {
        flex: 1,
      },
    },
  
    image: {
      flex: 1,
  
      [theme.fn.smallerThan('md')]: {
        display: 'none',
      },
    },
  
    highlight: {
      position: 'relative',
      backgroundColor: theme.colors.green[1],
      borderRadius: theme.radius.sm,
      padding: `${rem(4)} ${rem(12)}`,
    },

    makeGreen: {
        backgroundColor: theme.colors.green[6]
    }

  }));
  
  export default function IntroHeading() {
    const { classes } = useStyles();
    return (
      <div>
        <Container>
          <div className={classes.inner}>
            <div className={classes.content}>
                <Title className={classes.title}>
                    Tipping Report <span className={classes.highlight}>Example App</span> 💸
                </Title>
              <Text color="dimmed" mt="md">
                Example application to demonstrate how you can use Square's APIs to calculate 
                tip revenue sharing for you tippable team members. This is commonly referred to as 'Tip Pooling'
              </Text>
                <Paper shadow="xs" p="md" mt="md">
                    <Text>
                        The tips in this app are calculated using hours worked by the team.
                        When you run the report, and choose the start and end time of the shifts you would like to calculate, the app will do the following                        
                    </Text>
                    <List
              mt={30}
              spacing="sm"
              size="sm"
              icon={
                <ThemeIcon size={20} radius="xl" className={classes.makeGreen}>
                  <IconCheck size={rem(12)} stroke={1.5} />
                </ThemeIcon>
              }
            >
              <List.Item>
              1. Calculate the total hours worked by all team members during the given time range
              </List.Item>
              <List.Item>
              2. Calculate the total amount of tip money earned during the worked shifts for that time range
              </List.Item>
              <List.Item>
              3. Divde the total amount of tips by the total hours worked to get the amount of tippable money per hour
              </List.Item>
              <List.Item>
              4. For each team member, multiply the hours this team member worked by the amount derived in step 3 to get the amount of tip money the team member has earned
              </List.Item>
            </List>
            </Paper>
            </div>
          </div>
        </Container>
      </div>
    );
  }